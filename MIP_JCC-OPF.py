# Author: Alvaro Porras Cabrera
# Reduced Sample Average Approximation
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# This functions solves the SAA-based JCC-OPF
def opf_problem(data,valid):    
    # valid: the valid inequalities generated
    # data : class of the power system data
    
    # Model Parameters
    num_g   = data.T_units.shape[0]       # Number of generators
    num_l   = data.lines.shape[0]         # Number of lines
    Cost2   = data.T_units['c2'].values   # Quadratic coefficient of cost function
    Cost1   = data.T_units['c1'].values   # Linear    coefficient of cost function
    Cost0   = data.T_units['c0'].values   # Constant  coefficient of cost function
    Pmin_g  = data.T_units['Pmin'].values # Minimum capacity of generators
    Pmax_g  = data.T_units['Pmax'].values # Maximum capacity of generators
    Pmax_l  = data.lines['Pmax'].values   # Maximum capacity of lines
    PTDF    = data.ptdf.values            # PTDF matrix
    in_gen  = data.incidence_gen().values # Incidence matrix of generators 
    net_l   = data.nload['pred'].values   # Predicted net demand
    epsilon = data.epsilon                # Acceptable violation probability
    Mmin_g  = data.BMs['Mmin_g'].values   # Big-M of the lower bound constraint of generators
    Mmax_g  = data.BMs['Mmax_g'].values   # Big-M of the upper bound constraint of generators
    Mmin_l  = data.BMs['Mmin_l'].values   # Big-M of the lower bound constraint of lines
    Mmax_l  = data.BMs['Mmax_l'].values   # Big-M of the upper bound constraint of lines
    lin_gen  = PTDF @ in_gen
    lin_load = PTDF @ net_l 

    omega   = data.scenarios.T.sum().values
    variance= data.scenarios.T.sum().values.var()
    scen    = data.scenarios.values
    num_s   = data.scenarios.shape[0]
    lin_ome  = PTDF @ scen.T

    # Ordering Omegas to create the generators' valid inequalities
    omega_pmin  = data.scenarios.T.sum().sort_values(ascending=False).to_list()[int(epsilon*num_s)]
    omega_pmax  = data.scenarios.T.sum().sort_values().to_list()[int(epsilon*num_s)]

    # Create a new model
    model = gp.Model("MIP_CC-DC-OPF")
    
    # Model Variables
    gen    = model.addVars(num_g,lb=0.0,ub=float('inf'),vtype=GRB.CONTINUOUS,name="p")
    factor = model.addVars(num_g,lb=0.0,ub=float('inf'),vtype=GRB.CONTINUOUS,name="factor")
    y = model.addVars(num_s,vtype=GRB.BINARY,name="y")
 
    # Set objective
    obj_expr = gp.quicksum(Cost2[g]*(gen[g]**2 + variance*factor[g]**2) + Cost1[g]*gen[g] + Cost0[g] for g in range(num_g))
    model.setObjective(obj_expr, GRB.MINIMIZE) 
    
    # Balance Constraint
    model.addConstr(gen.sum() - net_l.sum() == 0)
    
    # Deterministic Constraints
    model.addConstrs((gen[g] >= Pmin_g[g] for g in range(num_g)))
    model.addConstrs((gen[g] <= Pmax_g[g] for g in range(num_g)))
    model.addConstrs((gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - lin_load[l] >= -Pmax_l[l] for l in range(num_l)))
    model.addConstrs((gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - lin_load[l] <=  Pmax_l[l] for l in range(num_l)))
     
    # Violated scenarios
    model.addConstr(y.sum() >= num_s - int(epsilon*num_s))
    
    # Participation Factor Constraint
    model.addConstr(factor.sum() == 1)

    # Generator Down Constraint
    model.addConstrs((gen[g] - omega[s]*factor[g] >= Pmin_g[g] - Mmin_g[s,g]*(1-y[s])  for g in range(num_g) for s in range(num_s) if Mmin_g[s,g]>0))
    
    # Generator Up Constraint
    model.addConstrs((gen[g] - omega[s]*factor[g] <= Pmax_g[g] + Mmax_g[s,g]*(1-y[s])  for g in range(num_g) for s in range(num_s) if Mmax_g[s,g]>0))
    
    # Power flow down
    model.addConstrs((gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - omega[s]*gp.LinExpr([(lin_gen[l,g],factor[g]) for g in range(num_g)]) - lin_load[l] + lin_ome[l,s] >= -Pmax_l[l] - Mmin_l[s,l]*(1-y[s]) for l in range(num_l) for s in range(num_s) if Mmin_l[s,l] > 0))
 
    # Power flow up
    model.addConstrs((gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - omega[s]*gp.LinExpr([(lin_gen[l,g],factor[g]) for g in range(num_g)]) - lin_load[l] + lin_ome[l,s] <=  Pmax_l[l] + Mmax_l[s,l]*(1-y[s]) for l in range(num_l) for s in range(num_s) if Mmax_l[s,l] > 0))

    # Valid Inequalities
    # Generator constraints (order the omega paramter)
    model.addConstrs((gen[g] - omega_pmin*factor[g] >= Pmin_g[g] for g in range(num_g)))
    model.addConstrs((gen[g] - omega_pmax*factor[g] <= Pmax_g[g] for g in range(num_g)))
    
    # Line constraints
    for l in range(num_l):
        for i in valid['min'][l].index:
            model.addConstr(gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - lin_load[l] + Pmax_l[l] >= valid['min'][l].at[i,'slope']*gp.LinExpr([(lin_gen[l,g],factor[g]) for g in range(num_g)]) + valid['min'][l].at[i,'inter'])
        for i in valid['max'][l].index:
            model.addConstr(gp.LinExpr([(lin_gen[l,g],gen[g]) for g in range(num_g)]) - lin_load[l] - Pmax_l[l] <= valid['max'][l].at[i,'slope']*gp.LinExpr([(lin_gen[l,g],factor[g]) for g in range(num_g)]) + valid['max'][l].at[i,'inter'])
    
    # model parameters
    model.setParam('TimeLimit',36000)
    model.setParam('MIPGap',1e-9)
    model.setParam('threads',6)

    # optimizing
    model.optimize()
    
    Solution = {}
    
    # Generator's Power
    Solution['power'] = pd.DataFrame()
    Solution['power']['p']      = np.array(model.getAttr('X', gen.values()))
    Solution['power']['factor'] = np.array(model.getAttr('X', factor.values()))
    
    # Scenario violation decision
    Solution['y'] = np.array(model.getAttr('X', y.values()))
    
    # Solver data
    Solution['OP_info'] = pd.DataFrame()
    Solution['OP_info'].loc['obj','value']         = model.ObjVal
    Solution['OP_info'].loc['time','value']        = model.Runtime
    Solution['OP_info'].loc['MIPGap','value']      = model.MIPGap*100
    Solution['OP_info'].loc['condition','value']   = model.status
    Solution['OP_info'].loc['nodes','value']       = model.NodeCount
    Solution['OP_info'].loc['constraints','value'] = model.NumConstrs
    

    return Solution
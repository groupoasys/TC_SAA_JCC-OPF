#Author: Alvaro Porras Cabrera
# Gurobipy implementation of tightening-screening model
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# This function provides a tighter big-M for scenario "i_scen"
def method(data,i_scen,valid):
    # valid: the valid inequalities generated
    # data : class of the power system data
    
    # Model Parameters
    num_g   = data.T_units.shape[0]       # number of generators
    num_l   = data.lines.shape[0]         # number of lines
    Pmin_g  = data.T_units['Pmin'].values # Pmin of generators
    Pmax_g  = data.T_units['Pmax'].values # Pmax of generators
    Pmax_l  = data.lines['Pmax'].values   # Maximum capacity of lines
    PTDF    = data.ptdf.values            # PTDF Matrix
    in_gen  = data.incidence_gen().values # Incidence matrix of generators
    net_l   = data.nload['pred'].values   # Predicted net demand
    Mmin_g  = data.BMs['Mmin_g'].values   # Big-M of the lower bound constraint of generators from previous iteration
    Mmax_g  = data.BMs['Mmax_g'].values   # Big-M of the upper bound constraint of generators from previous iteration
    Mmin_l  = data.BMs['Mmin_l'].values   # Big-M of the lower bound constraint of lines from previous iteration
    Mmax_l  = data.BMs['Mmax_l'].values   # Big-M of the upper bound constraint of lines from previous iteration
    epsilon = data.epsilon                # Acceptable violation probability
    lin_gen  = PTDF @ in_gen
    lin_load = PTDF @ net_l 

    omega   = data.scenarios.T.sum().values
    scen    = data.scenarios.values
    num_s   = data.scenarios.shape[0]
    lin_ome = PTDF @ scen.T
    
    # Ordering Omegas to create the generators' valid inequalities
    omega_pmin  = data.scenarios.T.sum().sort_values(ascending=False).to_list()[int(epsilon*num_s)]
    omega_pmax  = data.scenarios.T.sum().sort_values().to_list()[int(epsilon*num_s)]
            

    Solution = {}
    
    #Optimization Model
    model = gp.Model("Tightening-Screening_method_CC-DC-OPF")
            
    gen     = model.addVars(num_g,lb=0.0,ub=float('inf'),vtype=GRB.CONTINUOUS,name="p")
    factor  = model.addVars(num_g,lb=0.0,ub=float('inf'),vtype=GRB.CONTINUOUS,name='factor')
    y       = model.addVars(num_s,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS,name='y')
    
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
    
    # Solver parameters
    model.setParam('TimeLimit',10000)
    model.setParam('Predual',1)
    model.setParam('threads',6)   
    model.setParam('Method',3)  
    model.setParam('BarHomogeneous',1)
    model.setParam('ScaleFlag',2)
    
    Solution = {}
    Solution['time'] = pd.DataFrame()
    Solution['BM'] = {}
    for case in ['min','max']:
        Solution['BM'][case+'_g'] = pd.DataFrame(0,index=[i_scen],columns=range(num_g))
        Solution['BM'][case+'_l'] = pd.DataFrame(0,index=[i_scen],columns=range(num_l))

        if case == 'min':
            Solution['BM'][case+'_g'].loc[i_scen,:] = Mmin_g[i_scen,:]
            Solution['BM'][case+'_l'].loc[i_scen,:] = Mmin_l[i_scen,:]
        else:
            Solution['BM'][case+'_g'].loc[i_scen,:] = Mmax_g[i_scen,:]
            Solution['BM'][case+'_l'].loc[i_scen,:] = Mmax_l[i_scen,:]
            
        gen_index = Solution['BM'][case+'_g'].loc[i_scen,:][Solution['BM'][case+'_g'].loc[i_scen,:]>0 ].index.to_list()        
        lines_index = Solution['BM'][case+'_l'].loc[i_scen,:][Solution['BM'][case+'_l'].loc[i_scen,:]>0].index.to_list()

        if len(gen_index) > 0:# check if a generator constraint if redundant for scenario i_scen
            for g_i in gen_index:
            # Set objective
                if case == 'min':
                    model.setObjective(gen[g_i] - omega[i_scen]*factor[g_i], GRB.MINIMIZE)
                else:
                    model.setObjective(gen[g_i] - omega[i_scen]*factor[g_i], GRB.MAXIMIZE)
                           
                model.optimize()
                
                if model.status != 2:
                    print('########################################### Non optimal value found')
                    model.setParam('Method',1)
                    model.optimize()
                    model.setParam('Method',2)
              
                Solution['time'].loc[i_scen,case+'_gen-'+str(g_i)] = model.Runtime
                
                power = model.getAttr('X', gen.values())
                beta  = model.getAttr('X', factor.values())

                if case == 'min':
                    Solution['BM'][case+'_g'].loc[i_scen,g_i] = Pmin_g[g_i] - (power[g_i] - omega[i_scen]*beta[g_i])
                else:
                    Solution['BM'][case+'_g'].loc[i_scen,g_i] = (power[g_i] - omega[i_scen]*beta[g_i]) - Pmax_g[g_i]
                
                model.reset()
                print('###################### '+case+'_gen-'+str(g_i)+'_scenario-'+str(i_scen)+'_SC-') 
    
        if len(lines_index) > 0: # check if a line constraint if redundant for scenario i_scen 
            for line in lines_index:
            # Set objective
                if case == 'min':
                    model.setObjective(gp.LinExpr([(lin_gen[line,g],gen[g]) for g in range(num_g)]) - omega[i_scen]*gp.LinExpr([(lin_gen[line,g],factor[g]) for g in range(num_g)]) - lin_load[line] + lin_ome[line,i_scen], GRB.MINIMIZE)
                else:
                    model.setObjective(gp.LinExpr([(lin_gen[line,g],gen[g]) for g in range(num_g)]) - omega[i_scen]*gp.LinExpr([(lin_gen[line,g],factor[g]) for g in range(num_g)]) - lin_load[line] + lin_ome[line,i_scen], GRB.MAXIMIZE)               
                
                model.optimize()
                
                if model.status != 2:
                    print('########################################### Non optimal value found')
                    model.setParam('Method',1)
                    model.optimize()
                    model.setParam('Method',2)

                Solution['time'].loc[i_scen,case+'_line-'+str(line)] = model.Runtime
                
                power = model.getAttr('X', gen.values())
                beta  = model.getAttr('X', factor.values())

                if case == 'min':
                    Solution['BM'][case+'_l'].loc[i_scen,line] = -Pmax_l[line] - (lin_gen[line,:]@power - omega[i_scen]*lin_gen[line,:]@beta - lin_load[line] + lin_ome[line,i_scen])
                else:
                    Solution['BM'][case+'_l'].loc[i_scen,line] = -Pmax_l[line] + (lin_gen[line,:]@power - omega[i_scen]*lin_gen[line,:]@beta - lin_load[line] + lin_ome[line,i_scen])
                
                model.reset()
                print('###################### '+case+'_line-'+str(line)+'_scenario-'+str(i_scen)+'_SC-') 
    
    return Solution
    
            
            
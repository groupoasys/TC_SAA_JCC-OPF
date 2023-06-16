# Author: Alvaro Porras Cabrera
# Generating valid inequalities
import Inputs_Parameters as IP
import copy
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

# There are five systems (case) referred as the number of nodes
# There 10 different samples randomly generated, they are referred as seed_case

# Input Data- Choose one system and one sample
seed_case = range(10)[0]
case      = ['24','57','73','118','300'][0]

# Input Parameters
data = copy.deepcopy(IP.parameters(case)) # Input CSV data related to the systems
data.epsilon = 0.05                       # Acceptable violation probability

scenarios = pickle.load(open('Scenarios.pkl','rb'))
data.scenarios = scenarios[case][seed_case]

# Model Parameters
Pmax_l  = data.lines['Pmax'].values   # Maximum capacity of transmission lines
PTDF    = data.ptdf.values            # PTDF Matrix
in_gen  = data.incidence_gen().values # Incidence matrix of generators
net_l   = data.nload['pred'].values   # Predicted net demand
lin_gen  = PTDF @ in_gen 
lin_load = PTDF @ net_l 
epsilon = data.epsilon
num_s   = data.scenarios.shape[0]     # number of scenarios
num_l   = data.lines.shape[0]         # number of lines

valid = {}
lin_min_info = {}
lin_min_valid = {}
lin_max_info = {}
lin_max_valid = {}
support = pd.DataFrame()

for l in range(num_l):
    print('##################################### Line Number: ',l)
    lin_min_valid[l] = pd.DataFrame()
    lin_max_valid[l] = pd.DataFrame()
    lin_min_info[l] = pd.DataFrame()
    lin_max_info[l] = pd.DataFrame()
    omega   = data.scenarios.T.sum().values
    scen    = data.scenarios.values
    
    lin_ome = PTDF @ scen.T
    
    # z variable
    support.loc[l,'min'] = np.round(min(PTDF[l,:] @ in_gen),10) # z_min
    support.loc[l,'max'] = np.round(max(PTDF[l,:] @ in_gen),10) # z_max
    matrix_in = pd.DataFrame() # Intersections matrix (num_s,num_l)
    m = omega                  # slope
    n = -PTDF[l,:]@scen.T      # intercept
    
    # Check whether the intercepts are equal or the support of z is not empty
    if all(j==np.round(n[0],4) for j in np.round(n,4)) == False and support.at[l,'min'] != support.at[l,'max'] :
        for s in range(len(omega)):
            np.seterr(divide='ignore', invalid='ignore')
            matrix_in[s] = np.divide(n - n[s],m[s] - m)
        
        # ######## Minimum Power Flow Constraint
        x_list = []
        y_list = []
        scen_list = []
        
        # Getting the k-upper envelop
        # z where the intersection is located
        x_i = support.at[l,'min']
        # Scenarios where the envelop is placed
        scen_i = pd.DataFrame(omega*support.at[l,'min'] - PTDF[l,:]@scen.T)[0].nlargest(int(num_s*epsilon)+1).index.to_list()[-1]
        # Coordenate y
        y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        while x_i < support.at[l,'max']:
            x_list.append(x_i)
            y_list.append(y_i)
            scen_list.append(scen_i)
            x_i = matrix_in.loc[scen_i,:][matrix_in.loc[scen_i,:] > x_i].min()
            
            # If the intersection is caused by more than one line
            candidates = matrix_in.loc[scen_i,:][matrix_in.loc[scen_i,:] == x_i].index.to_list() + [scen_i]
            slope_cand = pd.DataFrame(omega[candidates],index=candidates)[0].sort_values()
            
            # Time to choose the next scenario in the envelop
            up_cand = sum(slope_cand < omega[scen_i])  # number of scenarios above the envelop 
            low_cand = sum(slope_cand > omega[scen_i]) # number of scenarios below the evenlop
            candidates = slope_cand.index.to_list()
            scen_i = candidates[candidates.index(scen_i) + low_cand - up_cand] # choosing the next scenario
            y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        x_i = support.at[l,'max']
        scen_i = pd.DataFrame(omega*support.at[l,'max'] - PTDF[l,:]@scen.T)[0].nlargest(int(num_s*epsilon)+1).index.to_list()[-1]
        y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        x_list.append(x_i)
        y_list.append(y_i)
        scen_list.append(scen_i)
            
        lin_min_info[l]['scen'] = scen_list
        lin_min_info[l]['x_bkp']  = x_list
        lin_min_info[l]['y_bkp']  = y_list
        
        # Convexifying by means of the lower hull
        i_min = lin_min_info[l]['y_bkp'].nsmallest(1).index[0]
        i_left = lin_min_info[l]['x_bkp'][lin_min_info[l]['x_bkp'] < lin_min_info[l].at[i_min,'x_bkp']].index.to_list()
        i_right = lin_min_info[l]['x_bkp'][lin_min_info[l]['x_bkp'] > lin_min_info[l].at[i_min,'x_bkp']].index.to_list()
        counter = 0
        while len(i_left) > 0:
            slopes = np.divide(lin_min_info[l].loc[i_left,'y_bkp']-lin_min_info[l].at[i_min,'y_bkp'],lin_min_info[l].loc[i_left,'x_bkp']-lin_min_info[l].at[i_min,'x_bkp'])
            i_slope= np.amax(slopes)
            i_inter= lin_min_info[l].at[i_min,'y_bkp'] - i_slope*lin_min_info[l].at[i_min,'x_bkp']
            lin_min_valid[l].at[counter,'slope'] = i_slope
            lin_min_valid[l].at[counter,'inter'] = i_inter
            i_min = np.argmax(slopes)
            i_left = range(i_min)
            counter += 1
            
        i_min = lin_min_info[l]['y_bkp'].nsmallest(1).index[0]
        while len(i_right) > 0:
            slopes = np.divide(lin_min_info[l].loc[i_right,'y_bkp']-lin_min_info[l].at[i_min,'y_bkp'],lin_min_info[l].loc[i_right,'x_bkp']-lin_min_info[l].at[i_min,'x_bkp'])
            i_slope= np.amin(slopes)
            i_inter= lin_min_info[l].at[i_min,'y_bkp'] - i_slope*lin_min_info[l].at[i_min,'x_bkp']
            lin_min_valid[l].loc[counter,'slope'] = i_slope
            lin_min_valid[l].loc[counter,'inter'] = i_inter
            i_min = i_right[np.argmin(slopes)]
            i_right = range(i_min+1,max(i_right)+1)
            counter += 1
        
        # ######## Maximum Power Flow Constraint
        x_list = []
        y_list = []
        scen_list = []
        
        # Getting the k-lower envelop
        x_i = support.at[l,'min']
        scen_i = pd.DataFrame(omega*support.at[l,'min'] - PTDF[l,:]@scen.T)[0].nsmallest(int(num_s*epsilon)+1).index.to_list()[-1]       
        y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        while x_i < support.at[l,'max']:
            x_list.append(x_i)
            y_list.append(y_i)
            scen_list.append(scen_i)
            x_i = matrix_in.loc[scen_i,:][matrix_in.loc[scen_i,:] > x_i].min()
            
            candidates = matrix_in.loc[scen_i,:][matrix_in.loc[scen_i,:] == x_i].index.to_list() + [scen_i]
            slope_cand = pd.DataFrame(omega[candidates],index=candidates)[0].sort_values()
            
            up_cand = sum(slope_cand < omega[scen_i])
            low_cand = sum(slope_cand > omega[scen_i])
            candidates = slope_cand.index.to_list()
            scen_i = candidates[candidates.index(scen_i) + low_cand - up_cand]
            y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        x_i = support.at[l,'max']
        scen_i = pd.DataFrame(omega*support.at[l,'max'] - PTDF[l,:]@scen.T)[0].nsmallest(int(num_s*epsilon)+1).index.to_list()[-1]
        y_i = omega[scen_i]*x_i - PTDF[l,:]@scen[scen_i,:]
        
        x_list.append(x_i)
        y_list.append(y_i)
        scen_list.append(scen_i)
        
        lin_max_info[l]['scen'] = scen_list
        lin_max_info[l]['x_bkp']  = x_list
        lin_max_info[l]['y_bkp']  = y_list
        
        # Convexifying by means of the upper hull
        i_max = lin_max_info[l]['y_bkp'].nlargest(1).index[0]
        i_left = lin_max_info[l]['x_bkp'][lin_max_info[l]['x_bkp'] < lin_max_info[l].at[i_max,'x_bkp']].index.to_list()
        i_right = lin_max_info[l]['x_bkp'][lin_max_info[l]['x_bkp'] > lin_max_info[l].at[i_max,'x_bkp']].index.to_list()
        counter = 0
        while len(i_left) > 0:
            slopes = np.divide(lin_max_info[l].loc[i_left,'y_bkp']-lin_max_info[l].at[i_max,'y_bkp'],lin_max_info[l].loc[i_left,'x_bkp']-lin_max_info[l].at[i_max,'x_bkp'])
            i_slope= np.amin(slopes)
            i_inter= lin_max_info[l].at[i_max,'y_bkp'] - i_slope*lin_max_info[l].at[i_max,'x_bkp']
            lin_max_valid[l].at[counter,'slope'] = i_slope
            lin_max_valid[l].at[counter,'inter'] = i_inter
            i_max = np.argmin(slopes)
            i_left = range(i_max)
            counter += 1
            
        i_max = lin_max_info[l]['y_bkp'].nlargest(1).index[0]
        while len(i_right) > 0:
            slopes = np.divide(lin_max_info[l].loc[i_right,'y_bkp']-lin_max_info[l].at[i_max,'y_bkp'],lin_max_info[l].loc[i_right,'x_bkp']-lin_max_info[l].at[i_max,'x_bkp'])
            i_slope= np.amax(slopes)
            i_inter= lin_max_info[l].at[i_max,'y_bkp'] - i_slope*lin_max_info[l].at[i_max,'x_bkp']
            lin_max_valid[l].loc[counter,'slope'] = i_slope
            lin_max_valid[l].loc[counter,'inter'] = i_inter
            i_max = i_right[np.argmax(slopes)]
            i_right = range(i_max+1,max(i_right)+1)
            counter += 1
            
    else:
        # if the intercept is equal, then it is just ordering slopes
        if support.at[l,'min'] != support.at[l,'max']:
            if support.at[l,'min'] == 0:
                lin_min_valid[l].loc[0,'slope'] = pd.DataFrame(omega)[0].nlargest(int(epsilon*num_s)+1).to_list()[-1]
                lin_min_valid[l].loc[0,'inter'] = 0
                lin_max_valid[l].loc[0,'slope'] = pd.DataFrame(omega)[0].nsmallest(int(epsilon*num_s)+1).to_list()[-1]
                lin_max_valid[l].loc[0,'inter'] = 0
            else:
                lin_min_valid[l].loc[0,'slope'] = pd.DataFrame(omega)[0].nsmallest(int(epsilon*num_s)+1).to_list()[-1]
                lin_min_valid[l].loc[0,'inter'] = 0
                lin_max_valid[l].loc[0,'slope'] = pd.DataFrame(omega)[0].nlargest(int(epsilon*num_s)+1).to_list()[-1]
                lin_max_valid[l].loc[0,'inter'] = 0
                
         # if the support of z is empty, then it is just ordering intercepts
        else:
            lin_min_valid[l].loc[0,'slope'] = 0
            lin_min_valid[l].loc[0,'inter'] = pd.DataFrame(n)[0].nlargest(int(epsilon*num_s)+1).to_list()[-1]
            lin_max_valid[l].loc[0,'slope'] = 0
            lin_max_valid[l].loc[0,'inter'] = pd.DataFrame(n)[0].nsmallest(int(epsilon*num_s)+1).to_list()[-1]
    
    # Filtering out segments with huge slopes (they can be considered outliers)
    index_l_po = lin_min_valid[l]['slope'][lin_min_valid[l]['slope']>max(omega)*2].index
    index_l_ne = lin_min_valid[l]['slope'][lin_min_valid[l]['slope']<min(omega)*2].index
    for i in index_l_po:
        lin_min_valid[l] = lin_min_valid[l].drop(axis=0,index=i)
    for i in index_l_ne:
        lin_min_valid[l] = lin_min_valid[l].drop(axis=0,index=i)
    
    index_l_po = lin_max_valid[l]['slope'][lin_max_valid[l]['slope']>max(omega)*2].index
    index_l_ne = lin_max_valid[l]['slope'][lin_max_valid[l]['slope']<min(omega)*2].index
    for i in index_l_po:
        lin_max_valid[l] = lin_max_valid[l].drop(axis=0,index=i)
    for i in index_l_ne:
        lin_max_valid[l] = lin_max_valid[l].drop(axis=0,index=i)
    
    # #Plot to represent the k-envelops
    # size = (10,6)
    # resolution = 100
    # size_sample = 1000
    # fig = plt.figure(num = l, figsize = size, dpi = resolution, facecolor = 'w', edgecolor = 'k')
    # x = np.linspace(support.at[l,'min'],support.at[l,'max'],1000)
    # quantile_min = []
    # quantile_max = []
    # for i in x:
    #     df = pd.DataFrame()
    #     df[0] = omega*i - PTDF[l,:]@scen.T
    #     quantile_min.append(df[0].nlargest(int(epsilon*num_s)+1).to_list()[-1])
    #     quantile_max.append(df[0].nsmallest(int(epsilon*num_s)+1).to_list()[-1])
    # for s in range(len(omega)):
    #     plt.plot(x, omega[s]*x - PTDF[l,:]@scen[s,:],color='blue', linewidth=0.5)
    # for i in lin_min_valid[l].index:
    #     plt.plot(x, lin_min_valid[l].at[i,'slope']*x + lin_min_valid[l].at[i,'inter'],color='green', linewidth=1.5)
    # for i in lin_max_valid[l].index:
    #     plt.plot(x, lin_max_valid[l].at[i,'slope']*x + lin_max_valid[l].at[i,'inter'],color='green', linewidth=1.5)  
    # plt.plot(x,quantile_min,'o',color='red')
    # plt.plot(x,quantile_max,'o',color='red')
    # plt.plot(lin_min_info[l]['x_bkp'].values,lin_min_info[l]['y_bkp'].values,'o',color='yellow')
    # plt.plot(lin_max_info[l]['x_bkp'].values,lin_max_info[l]['y_bkp'].values,'o',color='yellow')
    # plt.grid(True)
    # plt.ylabel("uncertainty",fontsize=22,fontname="Times New Roman")
    # plt.xlabel("parameter A",fontsize=22,fontname="Times New Roman")
    # plt.xticks(fontsize=22,ha='center',fontname="Times New Roman")
    # plt.yticks(fontsize=22,fontname="Times New Roman")
    # plt.title(case,fontsize=22,fontname="Times New Roman")
    # plt.axis()
    # plt.show()
    
    valid['min'] = lin_min_valid
    valid['max'] = lin_max_valid

# Save the results in pickle format
pickle_out = open('Valid_'+str(seed_case)+'_'+case+'.pkl',"wb")
pickle.dump(valid, pickle_out)
pickle_out.close()

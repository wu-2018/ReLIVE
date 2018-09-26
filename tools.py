import itertools
from collections import defaultdict, Counter
import numpy as np
import math

data = None

def scale_alpha(value, min_ = 0.1, max_ = 0.8):
    """Log2 minmax scale."""
    if len(value)==0:
        return []
    if len(value)==1:
        return [(min_+max_)/2]
    value = np.log2(value)
    MAX_ = max(value)
    MIN_ = min(value)
    return list((value - MIN_) * (max_ - min_)/(MAX_ - MIN_) + min_ )


def line_pos_generator(sx, sy, ex, ey, num, dec_digits = 3):
    """Input two endpoints coordinates and points number,
    return all the points coordinates so they'll form a straight line.
    
    Arguments:
    sx,sy -- start point x,y coordinate
    ex,ey -- end point x,y coordinate
    num -- number of total points
    dec_digits -- round coordinates to a given precision in decimal digits (default 0)
    """
    px = np.linspace(sx,ex,num).round(dec_digits)
    py = np.linspace(sy,ey,num).round(dec_digits)
    return list(px), list(py)

def circ_pos_generator(num, r):
    circ = [i*2*math.pi/num for i in range(num)]
    c_x = [r*math.cos(i) for i in circ]
    c_y = [r*math.sin(i) for i in circ]
    return c_x, c_y

def bezier(start, end, control, steps):
    """Generate points in a bezier curve. 
    x and y coordinates should be calculated respectively."""
    return [(1-s)**2*start + 2*(1-s)*s*control + s**2*end for s in steps]


def checkCache(key, dict_, path_func_args, path_func = bezier):
    """Save the endpoint coordinates and corresponding path points into a dict,
    so next time when we meet the same coordinates, the path points need not to be
    calculated again.
    """
    if key in dict_:
        return dict_[key]
    else:
        dict_[key] = path_func(*path_func_args)
        return dict_[key]


def bezier_path_points(eD_start, eD_end, nD_x, nD_y, nD_index, step=20, bias=8):
    """Calculate bezier curve points for each connection."""
    steps = [i/step for i in range(step+1)]
    xs, ys = [], []
    cacheDict_x = dict()
    cacheDict_y = dict()
    #### Get the x,y coordinates of endpoints in each connection
    for s,e in zip(eD_start, eD_end):
        s_x = nD_x[nD_index.index(s)]
        s_y = nD_y[nD_index.index(s)]
        e_x = nD_x[nD_index.index(e)]
        e_y = nD_y[nD_index.index(e)]
        #print((s_x,s_y),'----->',(e_x,e_y)) #check if the endpoints coordinates are right

        if s[0] == 'L':        # For edges between ligands and receptors
            xs.append(checkCache( (s_x,e_x), cacheDict_x, (s_x, e_x, (s_x+e_x)/2, steps) ))
            ys.append(checkCache( (s_y,e_y), cacheDict_y, (s_y, e_y, -10, steps) ))
        else:                  # For edges between cells and ligands/receptors
            if e[0] == 'L':    #Ligand nodes will be drawed on the left part of the plot
                xs.append(checkCache( (s_x,e_x), cacheDict_x, (s_x, e_x, s_x-bias, steps) ))       
            else:
                xs.append(checkCache( (s_x,e_x), cacheDict_x, (s_x, e_x, s_x+bias, steps) ))     
            ys.append(checkCache( (s_y,e_y), cacheDict_y, (s_y, e_y, 15, steps) ))
    
    return xs, ys

#### A decorator  
LR, RR = None, None
def judge(func):
    def inner(**kwargs):
        global LR, RR, Pre_nodeData, Pre_edgeData, eD_p_Data, inPairEdges_index, cc_nodeData, cc_edgeData
        if (LR, RR) != (kwargs['Ligand_Range'], kwargs['Receptor_Range']):
            Pre_nodeData, Pre_edgeData, eD_p_Data, inPairEdges_index, cc_nodeData, cc_edgeData = func(**kwargs)
        LR, RR = kwargs['Ligand_Range'], kwargs['Receptor_Range']
        if kwargs['tick_all'] != True:
            #choose part of the Data
            nodeData_onlyP = dict()
            edgeData_onlyP = dict() 
            for i,v in Pre_edgeData.items():
                edgeData_onlyP[i] = [v[ind] for ind in inPairEdges_index]
            nodeData_onlyP['index'] = sorted(list(set(edgeData_onlyP['start'] + edgeData_onlyP['end'])))
            nodeData_onlyP['name'] = [data.index2name[i] for i in nodeData_onlyP['index']]
            
            nodeData_onlyP, edgeData_onlyP = all_path(nodeData_onlyP, edgeData_onlyP, eD_p_Data, kwargs['node_ep'])
            return nodeData_onlyP, edgeData_onlyP, cc_nodeData, cc_edgeData
        else:
            nodeData_all, edgeData_all = all_path(Pre_nodeData, Pre_edgeData, eD_p_Data, kwargs['node_ep'])
            return nodeData_all, edgeData_all, cc_nodeData, cc_edgeData
    return inner


@judge
def updatePlotData(node_ep, tick_all, Ligand_Range, Receptor_Range):
    """When the ranges change, reselect the genes that will be shown on the plot, 
    also update the node positions, connections and their paths.

    Arguments:
    node_ep -- endpoint coordinates
    Ligand_Range, Receptor_Range -- Expression value range
    """
    
    ## Ligands & Receptors that are within the range
    x_l = np.where((data.l_fExpr > math.ceil(Ligand_Range[0])) & (data.l_fExpr < math.ceil(Ligand_Range[1])))
    x_r = np.where((data.r_fExpr > math.ceil(Receptor_Range[0])) & (data.r_fExpr < math.ceil(Receptor_Range[1])))


    ## Cells that has the ligand or receptor genes within the range
    ## Node index, use 'C','L','R' to distinguish cells, ligands and receptors
    c_i = ['C'+str(i) for i in set(x_l[1]).union(set(x_r[1]))]
    l_i = ['L'+str(i) for i in list(set(x_l[0]))]
    r_i = ['R'+str(i) for i in list(set(x_r[0]))]
    nD_index = c_i + l_i + r_i
    nD_name = [data.index2name[i] for i in nD_index]
    #### Put the information of nodes into a dict
    Pre_nodeData = dict(index = nD_index, name = nD_name)


    ## Start or end of a connection/edge must correspond with node index 
    eD_start_l = ['C' + str(x) for x in x_l[1]]
    eD_start_r = ['C' + str(x) for x in x_r[1]]
    eD_end_l = ['L' + str(x) for x in x_l[0]]
    eD_end_r = ['R' + str(x) for x in x_r[0]]
    eD_start = eD_start_l + eD_start_r
    eD_end = eD_end_l + eD_end_r

    eD_sn = [data.index2name[i] for i in eD_start]
    eD_en = [data.index2name[i] for i in eD_end]

    ## Get expression values
    l_value = [data.l_fExpr.iloc[i] for i in zip(x_l[0], x_l[1])]
    r_value = [data.r_fExpr.iloc[i] for i in zip(x_r[0], x_r[1])]
    eD_value = l_value + r_value
    ## L expressions are typically larger than R, so line alpha should be calculated respectively
    eD_scaled_alpha = scale_alpha(l_value) + scale_alpha(r_value)
    eD_sqrt_scaled_alpha = list(np.sqrt(eD_scaled_alpha))    
    #### Put the information of connections/edges into a dict
    Pre_edgeData = dict(start = eD_start, end = eD_end, start_name = eD_sn, end_name = eD_en, value = eD_value, 
                    scaled_alpha = eD_scaled_alpha, sqrt_scaled_alpha = eD_sqrt_scaled_alpha)


    ## Add L-R pair edges information into the edgeData
    lig = [data.index2name[i] for i in set(eD_end_l)]
    rec = [data.index2name[i] for i in set(eD_end_r)]
    l_r_edge = [(l,r) for l in lig for r in rec if (r in data.pairDict[l])]
    eD_p_sn = list(zip(*l_r_edge))[0] if len(l_r_edge) != 0 else []
    eD_p_en = list(zip(*l_r_edge))[1] if len(l_r_edge) != 0 else []
    eD_p_start = [data.name2index[l] for l in eD_p_sn]
    eD_p_end = [data.name2index[r] for r in eD_p_en]
    #print(eD_p_start, '--->', eD_p_end)
    eD_p_Data = dict(start = eD_p_start, end = eD_p_end, start_name = eD_p_sn, end_name = eD_p_en)

    inPairEdges_index = [i for i,v in enumerate(eD_end) if (v in set(eD_p_start + eD_p_end))]

    cc_nodeData, cc_edgeData = cc_plot_data(eD_end_l, eD_start_l, eD_end_r, eD_start_r, eD_p_start, eD_p_end) 
    return Pre_nodeData, Pre_edgeData, eD_p_Data, inPairEdges_index, cc_nodeData, cc_edgeData



def all_path(nodeData, edgeData, eD_p_Data, node_ep):
    #Calculate nodes positions
    index_prefix = [i[0] for i in nodeData['index']]
    node_index_num = Counter(index_prefix)
    cx,cy = line_pos_generator(*node_ep['c'], node_index_num['C'])
    lx,ly = line_pos_generator(*node_ep['l'], node_index_num['L'])
    rx,ry = line_pos_generator(*node_ep['r'], node_index_num['R'])
    nD_x = cx+lx+rx
    nD_y = cy+ly+ry
    nodeData['x'] = nD_x
    nodeData['y'] = nD_y 

    ## Path for edge
    eD_xs, eD_ys = bezier_path_points(edgeData['start'], edgeData['end'], nD_x, nD_y, nodeData['index'])
    edgeData['xs'] = eD_xs
    edgeData['ys'] = eD_ys
    ## Add LR-edges to the edgeData
    eD_p_xs, eD_p_ys = bezier_path_points(eD_p_Data['start'], eD_p_Data['end'], nD_x, nD_y, nodeData['index'])
    edgeData['xs'].extend(eD_p_xs)
    edgeData['ys'].extend(eD_p_ys)
    LR_edge_num = len(eD_p_xs)
    edgeData['display'] = [' ']*len(edgeData['start']) + ['none']*LR_edge_num
    edgeData['sqrt_scaled_alpha'].extend([0.8]*LR_edge_num)
    edgeData['scaled_alpha'].extend([0.5]*LR_edge_num)
    edgeData['value'].extend([None]*LR_edge_num)
    for k,v in eD_p_Data.items():
        edgeData[k].extend(v)
    #nodeData['show_l'] = ['*']*len(nD_index)
    return nodeData, edgeData



def cc_plot_data(eD_end_l, eD_start_l, eD_end_r, eD_start_r, eD_p_start, eD_p_end):

    ## To get something like {'L132': ['C7', 'C8', 'C16'], 'L188': ['C17']}
    l_c_D = defaultdict(list)
    r_c_D = defaultdict(list)
    for a,b in zip(eD_end_l, eD_start_l):
        l_c_D[a].append(b)
    for a,b in zip(eD_end_r, eD_start_r):
        r_c_D[a].append(b)

    ## cc_D {('C16', 'C16'): ['L84-->R331','L95-->R331'], ('C18', 'C16'): ['L258-->R372']}
    cc_D = defaultdict(list)
    for l,r in zip(eD_p_start, eD_p_end):
        for i in itertools.product(l_c_D[l], r_c_D[r]):
            cc_D[i].append(data.index2name[l]+'-->'+data.index2name[r])
    
    cc_nD_index = list(set(i for ii in cc_D.keys() for i in ii))
    cc_nD_name = [data.index2name[i] for i in cc_nD_index]
    cc_x, cc_y = circ_pos_generator(len(cc_nD_index), 10)
    cc_lx, cc_ly = circ_pos_generator(len(cc_nD_index), 10+1)
    cc_nodeData = dict(index=cc_nD_index, name=cc_nD_name, x=cc_x, y=cc_y, lx=cc_lx, ly=cc_ly)

    cc_nodes_pos = dict(zip(cc_nD_index, zip(cc_x, cc_y)))
    
    r_s = 1.5
    r_prop_coef = (r_s+10)/10
    xs_, ys_ = circ_pos_generator(30, r_s)
    xs_ += xs_[:2]
    ys_ += ys_[:2]
    cc_start, cc_end, cc_w, cc_tip, cc_xs, cc_ys = [], [], [], [], [], []
    for k,v in cc_D.items():
        cc_start.append(k[0])
        cc_end.append(k[1])
        cc_w.append(len(v))
        cc_tip.append(v)
        if k[0] == k[1]:
            x_pos, y_pos = cc_nodes_pos[k[0]]
            cc_xs.append([i+x_pos*r_prop_coef for i in xs_])
            cc_ys.append([i+y_pos*r_prop_coef for i in ys_])
        else:
            x_pos_s, y_pos_s = cc_nodes_pos[k[0]]
            x_pos_e, y_pos_e = cc_nodes_pos[k[1]]
            cc_xs.append([x_pos_s, x_pos_e])
            cc_ys.append([y_pos_s, y_pos_e])
    
    cc_sn, cc_en = [data.index2name[i] for i in cc_start], [data.index2name[i] for i in cc_end]
    cc_edgeData = dict(start=cc_start, end=cc_end, width=cc_w, start_name=cc_sn, end_name=cc_en,
                       tip=cc_tip, xs=cc_xs, ys=cc_ys)
    return cc_nodeData, cc_edgeData

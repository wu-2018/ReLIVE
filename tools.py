import numpy as np

def scale_alpha(value, min_ = 0.1, max_ = 0.8):
    """Log2 minmax scale."""
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
        if e[0] == 'L': #Ligand nodes will be drawed on the left part of the plot
            xs.append(checkCache( (s_x,e_x), cacheDict_x, (s_x, e_x, s_x-bias, steps) ))       
        else:
            xs.append(checkCache( (s_x,e_x), cacheDict_x, (s_x, e_x, s_x+bias, steps) ))     
        ys.append(checkCache( (s_y,e_y), cacheDict_y, (s_y, e_y, 13, steps) ))
    
    return xs, ys

#### Set expression thresholds for ligand and receptor genes respectively
##?! DEFAULT THRESHOLDS SHOULD BE BASED ON THE APPROPRIATE  NUMBER OF ELEMENTS PLOTED ON THE FIGURE


def updatePlotData(l_fExpr, r_fExpr, node_ep, Ligand_T=14, Receptor_T=3):
    """When the thresholds change, reselect the genes that will be shown on the plot, 
    also update the node positions, connections and their paths.

    Arguments:
    l_fExpr, r_fExpr -- filtered ligand and receptor expression dataframe
    node_ep -- endpoint coordinates
    Ligand_T, Receptor_T -- threshold
    """
    x_l = np.where(l_fExpr > Ligand_T)
    x_r = np.where(r_fExpr > Receptor_T)

    ## Ligands & Receptors that are above the threshold
    a_Thre_l = list(np.take(l_fExpr.index, list(set(x_l[0]))))
    a_Thre_r = list(np.take(r_fExpr.index, list(set(x_r[0]))))
    ## Cells that has the ligand or receptor genes above threshold
    c_i = list(set(x_l[1]).union(set(x_r[1])))
    a_Thre_c = list(np.take(l_fExpr.columns, c_i))

    ## Node index, use 'C','L','R' to distinguish cells, ligands and receptors
    nD_index = ['C'+str(i) for i in c_i] + \
               ['L'+str(i) for i in list(set(x_l[0]))] + \
               ['R'+str(i) for i in list(set(x_r[0]))]
    nD_name = a_Thre_c + a_Thre_l + a_Thre_r
    ## Calculate nodes positions
    cx,cy = line_pos_generator(*node_ep['c'], len(a_Thre_c))
    lx,ly = line_pos_generator(*node_ep['l'], len(a_Thre_l))
    rx,ry = line_pos_generator(*node_ep['r'], len(a_Thre_r))
    nD_x = cx+lx+rx
    nD_y = cy+ly+ry
    #### Put all information of nodes into a dict
    nodeData = dict(index = nD_index, name = nD_name, x = nD_x, y = nD_y )
    
    ## Start or end of a connection/edge must correspond with node index 
    eD_start = list(np.vectorize(lambda x: 'C' + str(x))(x_l[1])) +\
               list(np.vectorize(lambda x: 'C' + str(x))(x_r[1]))
    eD_end = list(np.vectorize(lambda x: 'L' + str(x))(x_l[0])) +\
             list(np.vectorize(lambda x: 'R' + str(x))(x_r[0]))
    ## Get expression values
    eD_value = [l_fExpr.iloc[i] for i in zip(x_l[0], x_l[1])] +\
               [r_fExpr.iloc[i] for i in zip(x_r[0], x_r[1])]
    ## Calculate path points for each edges
    eD_xs, eD_ys = bezier_path_points(eD_start, eD_end, nD_x, nD_y, nD_index)
    #### Put all information of connections/edges into a dict
    edgeData = dict(start = eD_start, end = eD_end, value = eD_value, xs = eD_xs, ys = eD_ys)
    
    return nodeData, edgeData

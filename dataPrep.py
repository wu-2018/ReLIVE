from os.path import dirname

import numpy as np
import pandas as pd
from collections import defaultdict

dir_ = dirname(__file__)

class DataPrep:
    
    def __init__(self, pD_file='/data/pairs.tsv', eD_file='/data/expr.tsv'):
        #### Read data
        self.pairData = pd.read_table(dir_ + pD_file)
        self.exprData = pd.read_table(dir_ + eD_file)

        #### Get a pair dict in the form like 'ligand':{'r1','r2','r3',...}
        Ligands = self.pairData.Ligand
        Receptors = self.pairData.Receptor
        
        self.pairDict = defaultdict(list)
        for i in range(len(self.pairData)):
            li = Ligands[i]
            self.pairDict[li].append(Receptors[i])
        #print(self.pairDict)
         
        #### Get gene set from the ligand-receptor data
        self.Ligands = set(Ligands)
        self.Receptors = set(Receptors)
        self.All_genes = self.Ligands.union(self.Receptors)
        #print(len(self.All_genes))
        #print(pd.value_counts(exprData.index.isin(self.All_genes)))

        self.input_gene_num, self.input_cell_num = self.exprData.shape

        #### Filter out genes that are not in the ligand-receptor database
        filteredExpr = self.exprData.loc[self.exprData.index.isin(self.All_genes), ]

        #### Discriminate between ligands and receptors
        gene_type = np.where(filteredExpr.index.isin(self.Ligands), 'ligand', 'receptor')
        ligandIndex = np.where(filteredExpr.index.isin(self.Ligands))[0]
        receptorIndex = np.where(~filteredExpr.index.isin(self.Ligands))[0]

        f_gene_num, f_cell_num = filteredExpr.shape
        filteredDict = dict(gene_index = list(range(f_gene_num)), gene_name = filteredExpr.index, 
                            gene_type = gene_type, cell_index = list(range(f_cell_num)), 
                            cell_name = filteredExpr.columns)

        self.l_fExpr = filteredExpr.iloc[ligandIndex, ]
        self.r_fExpr = filteredExpr.iloc[receptorIndex, ]

        L_index = ['L' + str(i) for i in range(self.l_fExpr.shape[0])]
        C_index = ['C' + str(i) for i in range(self.l_fExpr.shape[1])]
        R_index = ['R' + str(i) for i in range(self.r_fExpr.shape[0])]
        index = L_index + C_index + R_index              
        name =  list(self.l_fExpr.index) + list(self.l_fExpr.columns) + list(self.r_fExpr.index)
        self.index2name = dict(zip(index, name))
        self.name2index = dict(zip(name, index)) #!!! Be aware of duplicated names! Some preprocessing is needed!

        self.l_fExpr.index = L_index
        self.l_fExpr.columns = C_index
        self.r_fExpr.index = R_index
        self.r_fExpr.columns = C_index



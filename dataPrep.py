from os.path import dirname

import numpy as np
import pandas as pd
from collections import defaultdict

dir_ = dirname(__file__)
#### Read data
pairData = pd.read_table(dir_+'/data/pairs.tsv')
exprData = pd.read_table(dir_+'/data/expr.tsv')

#### Get a pair dict in the form like 'ligand':{'r1','r2','r3',...}
Ligands = pairData.Ligand
Receptors = pairData.Receptor

pairDict = defaultdict(list)
for i in range(len(pairData)):
    li = Ligands[i]
    pairDict[li].append(Receptors[i])
#print(pairDict)

#### Get gene set from the ligand-receptor data
Ligands = set(Ligands)
Receptors = set(Receptors)
All_genes = Ligands.union(Receptors)
#print(len(All_genes))
#print(pd.value_counts(exprData.index.isin(All_genes)))

input_gene_num, input_cell_num = exprData.shape

'''
## generate a dict for originally input expression matrix
#inputDict = dict(gene_index = range(gene_num), gene_name = exprData.index, 
#                 cell_index = range(cell_num), cell_name = exprData.columns)
'''

#### Filter out genes that are not in the ligand-receptor database
filteredExpr = exprData.loc[exprData.index.isin(All_genes), ]

#### Discriminate between ligands and receptors
gene_type = np.where(filteredExpr.index.isin(Ligands), 'ligand', 'receptor')
ligandIndex = np.where(filteredExpr.index.isin(Ligands))[0]
receptorIndex = np.where(~filteredExpr.index.isin(Ligands))[0]

f_gene_num, f_cell_num = filteredExpr.shape
filteredDict = dict(gene_index = list(range(f_gene_num)), gene_name = filteredExpr.index, 
                    gene_type = gene_type, cell_index = list(range(f_cell_num)), 
                    cell_name = filteredExpr.columns)

l_fExpr = filteredExpr.iloc[ligandIndex, ]
r_fExpr = filteredExpr.iloc[receptorIndex, ]


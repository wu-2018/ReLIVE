from os.path import dirname
import sys
import importlib.util

import dataPrep
import sidePlots

import pandas as pd

from bokeh.io import curdoc, show, output_file
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox, column
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, TapTool, \
     BoxSelectTool, ColumnDataSource, Div, ImageURL, LabelSet, CustomJS, CustomJSHover
from bokeh.models.widgets import RangeSlider, CheckboxGroup, Panel, Tabs, TextInput
from bokeh.models.graphs import NodesAndLinkedEdges, EdgesAndLinkedNodes

SPEC_TOOLS = importlib.util.find_spec('tools')
def reload_tools():
    tools = importlib.util.module_from_spec(SPEC_TOOLS)
    SPEC_TOOLS.loader.exec_module(tools)
    return tools

args = curdoc().session_context.request.arguments
try:
    F = args.get('F')[0].decode()
    tools = reload_tools()
    tools.data = dataPrep.DataPrep(eD_file="/data/uploads/"+F)
except:
    tools = reload_tools()
    tools.data = dataPrep.DataPrep()

#### Transfer the data into Module `tools` for further calculation
#tools.data = dataPrep.DataPrep()
#### Min and max value of the expression matrix
L_max = max(tools.data.l_fExpr.values.flatten())
R_max = max(tools.data.r_fExpr.values.flatten())
L_min = min(tools.data.l_fExpr.values.flatten())
R_min = min(tools.data.r_fExpr.values.flatten())

#### x&y coordinates range for each part: cells(upper), ligands(left) and receptors(right) 
node_ep = dict(c=[5,4,5,13], l=[3,0,-4,-10], r=[7,0,14,-10])

#### Set interactive widgets
#### Choose expression range of ligand and receptor genes respectively
l_RS_value = (27,139)
r_RS_value = (5,60)
l_RangeSlider = RangeSlider(title="Range of Ligand Expression", value=l_RS_value, start=int(L_min), end=int(L_max)+1, step=1)
r_RangeSlider = RangeSlider(title="Range of Receptor Expression", value=r_RS_value, start=int(R_min), end=int(R_max)+1, step=1)
##
checkbox_group = CheckboxGroup(labels=["op"], active=[], css_classes=['bk-cb'], name="bk_cb")
#### Dense plot for Gene expression distribution
l_d = dict(e_min=int(L_min), e_max=int(L_max)+1, value=l_RS_value, max_exprs=tools.data.l_fExpr.max(axis=1))
r_d = dict(e_min=int(R_min), e_max=int(R_max)+1, value=r_RS_value, max_exprs=tools.data.r_fExpr.max(axis=1))

s_plot_l = sidePlots.side_plot(l_d, l_RangeSlider)
s_plot_r = sidePlots.side_plot(r_d, r_RangeSlider)

#### the Main Plot
plot = figure(plot_width=1000, plot_height=600, x_range=(-5,17), y_range=(-12,15), tools="")
#plot.title.text = "Ligand-Receptor Interaction"
plot.min_border_left = 70
plot.grid.visible = False
plot.axis.visible = False
graphA = GraphRenderer()

nodeSource = graphA.node_renderer.data_source
graphA.node_renderer.glyph = Circle(size=12, fill_color='#a3a3cc')
graphA.node_renderer.selection_glyph = Circle(fill_color='#ccccff')
graphA.node_renderer.hover_glyph = Circle(fill_color='yellow')

edgeSource = graphA.edge_renderer.data_source
graphA.edge_renderer.glyph = MultiLine(line_color="#c98496", line_alpha='scaled_alpha', line_width=4.5)
graphA.edge_renderer.selection_glyph = MultiLine(line_color='#55c2b7', line_alpha='sqrt_scaled_alpha', line_width=6.5)
graphA.edge_renderer.nonselection_glyph = MultiLine(line_color="#c98496", line_alpha=0.15, line_width=2.5)
graphA.edge_renderer.hover_glyph = MultiLine(line_color='#a0d6b4', line_alpha=0.6, line_width=6.5)

#### Tooptips when hovering mouse on edges
TOOLTIPS = '''
    <div style="display:@display;">
        <p style="font-size:1.1em; font-weight:bold; margin:0px; padding:0px;">@start_name </br>
            <span style="color:#488ebc; font-size:1.1em; font-weight:bold">@end_name</span></br>
            <span style="font-size:0.9em; white-space:nowrap;">Expr_value: @value</span>
        </p>
    </div>
    <div style="display:@display{custom};">
        <p style="font-size:1.1em; font-weight:bold; margin:0px; padding:0px;">
            <span style="color:#488ebc; font-size:1.1em; font-weight:bold; white-space:nowrap;">
                @start_name ---- @end_name
            </span></br>
        </p>
    </div>
'''
## Display disparate tooltip contents for cells-genes edges and L-R pairs edges
cus_tt = CustomJSHover(code = '''
    if (value==" ") {return "none"}
    else if (value=="none") {return " "}
''')

hover= HoverTool(renderers = [graphA], tooltips=TOOLTIPS, show_arrow=False, formatters=dict(display=cus_tt))
plot.add_tools(hover, TapTool())
graphA.selection_policy = NodesAndLinkedEdges()
graphA.inspection_policy = EdgesAndLinkedNodes()
plot.renderers.append(graphA)

labels = LabelSet(x='x', y='y', text='name', text_color='#00cadb', x_offset=15, y_offset=1, source=nodeSource)
plot.add_layout(labels)
tab1 = Panel(child=plot, title="Cell-Gene Plot")

#### Cell-Cell plot
r = 10
cc_plot=figure(plot_width=720,plot_height=630,tools="",x_range=(-r-3.5,r+3.5),y_range=(-r-3.5,r+3.5),name="cc_plot")
cc_plot.min_border_left = 70
cc_plot.grid.visible = False
cc_plot.axis.visible = False
graphB=GraphRenderer()
cc_nS = graphB.node_renderer.data_source
cc_eS = graphB.edge_renderer.data_source

graphB.node_renderer.glyph = Circle(size=16, fill_color='#a3a3cc')
graphB.node_renderer.selection_glyph = Circle(fill_color='#ccccff')
graphB.node_renderer.hover_glyph = Circle(fill_color='yellow')
graphB.edge_renderer.glyph = MultiLine(line_color="#ffa200",line_width='width', line_alpha=0.7)#,line_join='miter')
graphB.edge_renderer.selection_glyph = MultiLine(line_color='#55c2b7', line_width='width')
graphB.edge_renderer.nonselection_glyph = MultiLine(line_color="#c98496", line_alpha=0.15, line_width='width')
graphB.edge_renderer.hover_glyph = MultiLine(line_color='#2f92d7', line_alpha=0.85, line_width='width')

cc_TOOLTIPS = """<div><p style="font-size:1.1em; font-weight:bold; margin:0px; padding:0px;">
            <span style="color:#488ebc; font-size:1.1em; font-weight:bold; white-space:nowrap;">
                @start_name ---- @end_name
            </span></br></p><p>@tip</p></div>
"""
cc_hover= HoverTool(renderers = [graphB], tooltips=cc_TOOLTIPS , show_arrow=False)
cc_plot.add_tools(cc_hover, TapTool())

graphB.selection_policy = NodesAndLinkedEdges()
graphB.inspection_policy = EdgesAndLinkedNodes()
'''
x_start=[i[0] for i in p_start]
y_start=[i[1] for i in p_start]
x_end=[i[0] for i in p_end]
y_end=[i[1] for i in p_end]

for i in range(len(x_start)):
    p.add_layout(Arrow(end=OpenHead(line_color="firebrick", line_width=4,size=7),
                   x_start=x_start[i], y_start=y_start[i], 
                   x_end=x_end[i], y_end=y_end[i]))
'''
cc_labels = LabelSet(x='lx', y='ly', text='name', text_color='#00cadb', text_align='center', y_offset=-13, source=cc_nS)
cc_plot.add_layout(cc_labels)
cc_plot.renderers.append(graphB)
tab2 = Panel(child=cc_plot, title="Cell-Cell Plot")

####
def update():
    tick_all = False if checkbox_group.active==[] else True
    nd, ed, cc_nd, cc_ed = \
    tools.updatePlotData(node_ep=node_ep, tick_all=tick_all, 
                         Ligand_Range=l_RangeSlider.value, Receptor_Range=r_RangeSlider.value)
    nodes_pos = dict(zip(nd['index'], zip(nd['x'], nd['y'])))
    graphA.layout_provider = StaticLayoutProvider(graph_layout=nodes_pos)
    
    cc_nodes_pos = dict(zip(cc_nd['index'], zip(cc_nd['x'], cc_nd['y'])))
    graphB.layout_provider = StaticLayoutProvider(graph_layout=cc_nodes_pos)

    nodeSource.data, edgeSource.data = nd, ed
    cc_nS.data, cc_eS.data = cc_nd, cc_ed

    #p_start=[nP[i] for i in cc_start]
    #p_end=[nP[i] for i in cc_end]
    #nodeSource.data['show_l'] = ['']*len(nodeSource.data['index'])
    
    ## For debugging. Check if the source data are generated correctly.
    #pd.DataFrame(edgeSource.data).to_csv('edge.csv')
    #pd.DataFrame(nodeSource.data).to_csv('node.csv')

controls = [l_RangeSlider, r_RangeSlider]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
checkbox_group.on_change('active',lambda attr, old, new: update())

left_side = column(s_plot_l.show(), s_plot_r.show(), name='left_side')
tabs = Tabs(tabs=[tab2, tab1], name="main_plots")
update()
for i in [left_side, tabs, checkbox_group]:
    curdoc().add_root(i)
curdoc().template_variables["flask_server"] = sys.argv[1]

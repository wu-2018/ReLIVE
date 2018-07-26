from os.path import dirname

import dataPrep
import tools
import pandas as pd

from bokeh.io import curdoc, show, output_file, reset_output, output_notebook
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, TapTool, \
     BoxSelectTool, ColumnDataSource, Div, ImageURL, LabelSet
from bokeh.models.widgets import Slider
from bokeh.models.graphs import NodesAndLinkedEdges, EdgesAndLinkedNodes

#### Set interactive widgets
l_T_Slider = Slider(title="Threshold for Ligand Expression (UMI)", value=14, start=0, end=100, step=1)
r_T_Slider = Slider(title="Threshold for Receptor Expression (UMI)", value=3, start=0, end=50, step=1)

#### Create 
TOOLTIPS=[
    ("Connect","@start--->@end"),
    ("Expr", "@value"),
    ("Coordinate", "$x, $y"),
]

#### Plot
plot = figure(plot_width=800, plot_height=600, x_range=(-5,15), y_range=(-12,12), tools="")
plot.title.text = "Ligand-Receptor Interaction"
graphA = GraphRenderer()

nodeSource = graphA.node_renderer.data_source
graphA.node_renderer.glyph = Circle(size=15, fill_color='#a3a3cc')
graphA.node_renderer.selection_glyph = Circle(fill_color='#ccccff')
graphA.node_renderer.hover_glyph = Circle(fill_color='yellow')

#nodes_pos = dict(zip(nodeSource.data['index'], zip(nodeSource.data['x'], nodeSource.data['y'])))
#graphA.layout_provider = StaticLayoutProvider(graph_layout=nodes_pos)

edgeSource = graphA.edge_renderer.data_source
graphA.edge_renderer.glyph = MultiLine(line_color="#c98496", line_alpha=0.5, line_width=5)
graphA.edge_renderer.selection_glyph = MultiLine(line_color='#55c2b7', line_alpha=0.5, line_width=10)
graphA.edge_renderer.hover_glyph = MultiLine(line_color='#a0d6b4', line_alpha=0.5, line_width=10)


#
#cells_TOOPTIPS = '''<div><p>Cell: @start</p><p>Expr_value: @expr_value</p></div>'''
#hover_on_cells= HoverTool(renderers = [graph_cells], tooltips=[('info','@tips')])
hover= HoverTool(renderers = [graphA], tooltips=TOOLTIPS, show_arrow=False)


plot.add_tools(TapTool(), hover )


graphA.selection_policy = NodesAndLinkedEdges()
graphA.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(graphA)

####
node_ep = dict(c=[5,5,5,10], l=[4,0,-3,-10], r=[6,0,13,-10])
####
def update():
    nodeSource.data, edgeSource.data = \
    tools.updatePlotData(dataPrep.l_fExpr, dataPrep.r_fExpr, node_ep, l_T_Slider.value, r_T_Slider.value)
    nodes_pos = dict(zip(nodeSource.data['index'], zip(nodeSource.data['x'], nodeSource.data['y'])))
    graphA.layout_provider = StaticLayoutProvider(graph_layout=nodes_pos)
    
    ## For debugging. Check if the source data are generated correctly.
    #pd.DataFrame(edgeSource.data).to_csv('edge.csv')
    #pd.DataFrame(nodeSource.data).to_csv('node.csv')

controls = [l_T_Slider, r_T_Slider]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())
#html template
with open(dirname(__file__)+"/description.html") as f:
    text = f.read()
desc = Div(text = text, width = 800)

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)

#div layout/position in the final html
l = layout([
    [desc],
    [inputs, plot],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Ligand-Receptor Interaction"


from os.path import dirname

import dataPrep
import tools
import sidePlots

import pandas as pd

from bokeh.io import curdoc, show, output_file
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox, column
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, TapTool, \
     BoxSelectTool, ColumnDataSource, Div, ImageURL, LabelSet, CustomJS, CustomJSHover
from bokeh.models.widgets import RangeSlider
from bokeh.models.graphs import NodesAndLinkedEdges, EdgesAndLinkedNodes

#### Min and max value of the expression matrix
L_max = max(dataPrep.l_fExpr.values.flatten())
R_max = max(dataPrep.r_fExpr.values.flatten())
L_min = min(dataPrep.l_fExpr.values.flatten())
R_min = min(dataPrep.r_fExpr.values.flatten())

#### Set interactive widgets
l_RS_value = (74,139)
r_RS_value = (15,60)
l_RangeSlider = RangeSlider(title="Range for Ligand Expression", value=l_RS_value, start=int(L_min), end=int(L_max)+1, step=1)
r_RangeSlider = RangeSlider(title="Range for Receptor Expression", value=r_RS_value, start=int(R_min), end=int(R_max)+1, step=1)

#### Dense plot for Gene expression distribution
l_d = dict(e_min=int(L_min), e_max=int(L_max)+1, value=l_RS_value, max_exprs=dataPrep.l_fExpr.max(axis=1))
r_d = dict(e_min=int(R_min), e_max=int(R_max)+1, value=r_RS_value, max_exprs=dataPrep.r_fExpr.max(axis=1))

s_plot_l = sidePlots.side_plot(l_d, l_RangeSlider)
s_plot_r = sidePlots.side_plot(r_d, r_RangeSlider)

#### Main Plot
plot = figure(plot_width=800, plot_height=600, x_range=(-5,17), y_range=(-12,15), tools="")
plot.title.text = "Ligand-Receptor Interaction"
plot.min_border_left = 70
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

JS_CODE ="""
    var inds = cb_obj.selected.indices;
    var data = cb_obj.data;
    console.log('hi'); 
    for (var i=0; i<inds.length; i++){
        data['show_l'][inds[i]]=data['name'][inds[i];]
    }
    cb_obj.change.emit();
    """
#nodeSource.callback = CustomJS(code=JS_CODE)


js2code='''
        console.log("hi!!!!");

        '''

js2 = CustomJS(code=js2code)
plot.add_tools(TapTool(callback=js2), hover, BoxSelectTool(callback=js2))

graphA.selection_policy = NodesAndLinkedEdges()
graphA.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(graphA)

labels = LabelSet(x='x', y='y', text='name', text_color='#00cadb', x_offset=15, y_offset=1, source=nodeSource)
plot.add_layout(labels)

####
node_ep = dict(c=[5,4,5,13], l=[3,0,-4,-10], r=[7,0,14,-10])

####
def update():
    nodeSource.data, edgeSource.data = \
    tools.updatePlotData(dataPrep.l_fExpr, dataPrep.r_fExpr, dataPrep.pairDict, node_ep, l_RangeSlider.value, r_RangeSlider.value)
    
    nodes_pos = dict(zip(nodeSource.data['index'], zip(nodeSource.data['x'], nodeSource.data['y'])))
    graphA.layout_provider = StaticLayoutProvider(graph_layout=nodes_pos)
    
    #nodeSource.data['show_l'] = ['']*len(nodeSource.data['index'])
    
    ## For debugging. Check if the source data are generated correctly.
    #pd.DataFrame(edgeSource.data).to_csv('edge.csv')
    #pd.DataFrame(nodeSource.data).to_csv('node.csv')
    

controls = [l_RangeSlider, r_RangeSlider]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

#html template
with open(dirname(__file__)+"/description.html") as f:
    text = f.read()
desc = Div(text = text, width = 800)

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

#inputs = widgetbox(*controls, sizing_mode=sizing_mode)

left_side = column(s_plot_l.show(), s_plot_r.show())

#div layout/position in the final html
l = layout([
    [desc],
    [left_side, plot],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Ligand-Receptor Interaction"


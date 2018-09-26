from bokeh.layouts import column, row
from bokeh.events import ButtonClick
from bokeh.models import CustomJS, ColumnDataSource, Span, Button, Band
from bokeh.plotting import figure
from bokeh.io import show
from scipy import stats

class side_plot:
    '''Interactive probability dense plot that changes with the attached slider value'''
    def __init__(self, infoDict, slider):
        self.iD = infoDict
        self.slider = slider
        
        x = list(range(self.iD['e_min'], self.iD['e_max']+1))
        p_d = list(stats.gaussian_kde(self.iD['max_exprs'])(x))
        
        v0, v1 = self.iD['value']
        x_i = x[v0:v1+1]
        y_i = p_d[v0:v1+1]
        
        #source1, for yellow highlighted area; source2, for grey colored area
        source1 = ColumnDataSource(data=dict(x_=x_i, y_l=[0]*len(x_i), y_u=y_i))
        source2 = ColumnDataSource(data=dict(x_=x[:1]+x+x[-1:], y_=[0]+p_d+[0]))
        
        self.p = figure(title="Probability density", tools="", background_fill_color="#ffffff", plot_height=210, plot_width=350, logo=None)
        self.p.x_range.range_padding=0.01
        self.p.y_range.range_padding=0
        
        ## Draw grey colored area
        self.p.patch('x_', 'y_', source=source2, color="#000000", alpha=0.2, line_width=0)
        
        ## Add Green dashlines 
        self.leftSpan = Span(location=self.slider.value[0], dimension='height', line_color='green',line_dash='dashed', line_width=3)
        self.rightSpan = Span(location=self.slider.value[1], dimension='height', line_color='green',line_dash='dashed', line_width=3)
        
        callback = CustomJS(args=dict(source1=source1, source2=source2, ran=(self.iD['e_min'], self.iD['e_max']),
                              x=x, p_d=p_d, leftSpan=self.leftSpan, rightSpan=self.rightSpan), code="""
                    var f0 = Math.ceil(cb_obj.value[0])
                    var f1 = Math.ceil(cb_obj.value[1])
                    var pad_i = 10
                    var pad_l = Math.min(f0-ran[0], pad_i)
                    var pad_r = Math.min(ran[1]-f1, pad_i)
                    //console.log(pad_l)
                    //console.log(pad_r)
                    var x_s = x.slice(f0,f1+1)
                    var y_s = p_d.slice(f0,f1+1)    
                    
                    leftSpan.location = f0
                    rightSpan.location = f1
                    
                    source1.data['x_'] = x_s
                    source1.data['y_u'] = y_s
                    source1.data['y_l'] = []
                    for (var i = 0; i < x_s.length; i++){source1.data['y_l'].push(0)}

                    source2.data['x_'] = x.slice(f0-pad_l,f1+1+pad_r)
                    source2.data['x_'].unshift(source2.data['x_'][0])
                    source2.data['x_'].push(source2.data['x_'][source2.data['x_'].length-1])

                    source2.data['y_'] = p_d.slice(f0-pad_l,f1+1+pad_r)
                    source2.data['y_'].unshift(0)
                    source2.data['y_'].push(0)

                    source2.change.emit()
                    source1.change.emit()             
                    """)
        self.slider.js_on_change('value', callback)
        
        ## Value reset button for RangeSlider 
        self.btn = Button(label="Reset", width=3, height=6)
        self.btn.js_on_event(ButtonClick, CustomJS(args=dict(value=self.iD['value'], slider=self.slider, 
                                          source2=source2, x_=x[:1]+x+x[-1:], y_=[0]+p_d+[0]),
                                          code='''slider.value=value
                                                  source2.data['x_']=x_
                                                  source2.data['y_']=y_
                                                  source2.change.emit()
                                               '''))
        ## Yellow highlight area
        self.band = Band(base='x_', lower='y_l', upper='y_u', source=source1, level='glyph', fill_alpha=1.0, line_width=1, line_color='black')
        
    def show(self):
        #print(self.iD)
        self.p.add_layout(self.band)
        self.p.add_layout(self.leftSpan)
        self.p.add_layout(self.rightSpan)
        
        tool = row(self.slider, self.btn)
        self.layout = column(tool, self.p)
        #show(self.layout)
        return self.layout

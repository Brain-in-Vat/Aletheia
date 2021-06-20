'''
1. 系统哪些状态需要展示给用户
    a 地址相关的代币分布
    b 治理损失函数的变化
    c 治理相关的数据

可视化工具
https://altair-viz.github.io/gallery/scatter_tooltips.html
https://seaborn.pydata.org/tutorial/relational.html
mesa
dash
'''

'''
共有的格式

私有的格式
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
df = px.data.iris()

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="scatter-plot"),
    html.P("Petal Width:"),
    dcc.RangeSlider(
        id='range-slider',
        min=0, max=2.5, step=0.1,
        marks={0: '0', 2.5: '2.5'},
        value=[0.5, 2]
    ),
])


@app.callback(
    Output("scatter-plot", "figure"),
    [Input("range-slider", "value")])
def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (df['petal_width'] > low) & (df['petal_width'] < high)
    fig = px.scatter(
        df[mask], x="sepal_width", y="sepal_length",
        color="species", size='petal_length',
        hover_data=['petal_width'])
    return fig


app.run_server(debug=True)

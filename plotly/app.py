# install dash / plotly / pandas
# !pip install dash jupyter-dash pandas

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#%% IMPORT

from turtle import title
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import util_plotly

app = Dash(__name__)

#%% LOAD DATAFRAME
df_path = "/home/gatis/Documents/random/RGB_project_plotly/plotly/inverted_wc2019.csv"
df = pd.read_csv(df_path,low_memory=False)

failed_id_path = "/home/gatis/Documents/random/RGB_project_plotly/plotly/failed_lift_id_2022_07_15__14_57.json"
successful_id_path = "/home/gatis/Documents/random/RGB_project_plotly/plotly/successful_lift_id_2022_07_15__15_09.json"

lift_dict_failed = util_plotly.load_json(failed_id_path)
lift_dict_successful = util_plotly.load_json(successful_id_path)



#%% CREATE THE FIGURE TO BE OUTPUT
def plot_feature_given_id_list_centered(lift_id_list,df_orig,title,feature_column = "y0"):
    """
    Given a list of ids plots all the lifts given feature column using "plotly".
    All the lifts are aligned by the local maximum in the y0 (nose).
    """
    df = df_orig.copy(deep=True)
    fig = go.Figure()

    for id_value in lift_id_list:

            # create a df with only the values for this id.
            df_plot = df[df["id"]==id_value].copy()

            # Find the peak value in the nose feature
            peak = df_plot["y0"].max()

            # Find the index fpr the [eak value]
            index_value = df_plot[df_plot["y0"] == peak].index.to_list()[0]
            index_value = index_value - df_plot.index[0]
            
            start = 0 - index_value
            end = df_plot.shape[0] - index_value
            df_plot.index = range(start,end)
            
            name = "{}:{}".format(id_value,df_plot["name"][0])
            
            fig.add_trace(go.Scatter(y=df_plot[feature_column], x=df_plot.index, mode="markers",name=name))
    # format figure
    fig.update_layout(
        title = "{} - {}".format(len(lift_id_list),title)
    )

    return fig




#%% CREATE THE LAYOUT IN THE WEBAPP

app.layout = html.Div(children=[
    html.H1(children='Display showing the path of the lifts'),

    html.Div(children='''
        Experimenting, with creating a color change application
    '''),

    html.Br(),

    dcc.Graph(
        id='lifts-graph'
        # figure=fig
    ),
    # dcc.Slider(
    #     min = 1,
    #     max = len(lift_dict_successful["good"]),
    #     # max = 10,
    #     step = 10,
    #     value = 10,
    #     id = 'no-of-lifts-slider'
    # ),

    dcc.RangeSlider(
        min = 1,
        max = len(lift_dict_successful["good"]),
        step = 10,
        id = 'range-slider',
        value=[1,10],

    ),
    html.Div(id = 'color_output')
])



@app.callback(
    # Output(component_id='example-graph',component_property='children'),
    # Input(component_id='color_input',component_property='value')
    Output(component_id='lifts-graph',component_property='figure'),
    # Input(component_id='no-of-lifts-slider',component_property='value')
    Input(component_id='range-slider',component_property='value')
)


def update_figure(range_slider_value):
    fig = plot_feature_given_id_list_centered(
                                              lift_dict_successful["good"]
                                                [range_slider_value[0]:range_slider_value[-1]],
                                              df,
                                              "All lifts",
                                              feature_column='y0')
    fig.update_layout(transition_duration=500)

    return fig





if __name__ == '__main__':
    
    app.run_server(debug=True)

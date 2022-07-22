# install dash / plotly / pandas / dash_daq
# !pip install dash jupyter-dash pandas

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#%% IMPORT

import string
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import util_plotly
import dash_daq as daq
from copy import copy
from ast import literal_eval
import serial # for sending to the Arduino
from PIL import ImageColor # For converting from hex to RGB

ser = serial.Serial("/dev/ttyUSB1")
app = Dash(__name__)

#%% LOAD DATAFRAME

# Create the dataframe, that will be used for informing led behavior
led_strip_size = 46 # size of the 
df = pd.DataFrame()

df["led_frequency"] = np.random.randint(1,10,size = led_strip_size).tolist()

# Initial color list
colors_list = [
'#D7537F',
'#53D764',
'#D1D753',
'#D75853',
'#53A0D7'
]

df["color"] = np.random.choice(colors_list,led_strip_size)

def send_to_uc(df_orig:pd.DataFrame):
    # print(df_orig)
    df = df_orig.copy(deep=True) # make a copy of the df
    # df = df.sort_index(ascending=False) # Inverse the order, so that the order of lights would be correct
    list_to_send = df.rgb.to_list()
    
    # remove following [ ] ( ) ' " "
    string_to_send = str(list_to_send).replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace(" ","")
    # print(string_to_send)
    # print(ser.is_open)
    ser.write("{}\n".format(string_to_send).encode())

def hex_to_rgb(hex_str:str):
    return str(ImageColor.getcolor(hex_str,"RGB"))

def update_dataframe(df):

    # column with copy of the frequncy values as strings, to make them discrete
    df["led_index_str"] = df.index
    df["led_index_str"] = df["led_index_str"].apply(lambda x:str(x)) 
    df["rgb"] = df["color"].apply(hex_to_rgb)
    # Create a dsicrete color map
    list_of_values = df.color.to_list()
    color_map = {str(item):(list_of_values[item]) for item in range(len(list_of_values))}
    # print(color_map)


    fig = px.scatter(df,
                    x=df.index,
                    y="led_frequency",
                    color="led_index_str",
                    color_discrete_map=color_map,
                    
                    size = "led_frequency",

                    labels = {
                        "led_frequency":"Frequency",
                        "index":"LED number, total of {}".format(led_strip_size)
                        }
                    )

    fig.update_layout(
                    showlegend=False,
                    # clickmode
                    dragmode = 'select' # uses the box selector by default
                    )
    return fig

fig = update_dataframe(df)



app.layout = html.Div(children=[

    dcc.Graph(
        id='status-graph',
        figure=fig
    ),

    dcc.RadioItems(
        ["Adjust Frequency","Adjust Color"],"Adjust Color",id='adjustment-selector'
        ),

    html.Div(id = 'color-output'),

    dcc.Slider(
        id = 'range-slider',
        min = 1,
        max = 10,
        step = 1,
        value=10
    ),
    daq.ColorPicker(
        id = 'color-piker',
        value=dict(hex='#119DFF'),
        size = 800
    )

],
style={
        'textAlign': 'center',
        'display': 'inline-block'
        }

)


# !!!!!!  Callback for reading the selceted data from the graph
@app.callback(
    Output(component_id='color-output',component_property='children'),
    Input(component_id='status-graph',component_property='selectedData')
)

def select_leds(selectedData):
    try:
        selected_points_index = [index_val["x"] for index_val in selectedData["points"]]
        selected_points_index.sort()
    except:
        selected_points_index = "Nothing Selected"
    return str(selected_points_index)



# !!!!!!  Callback for updating the color of the points based on the 
@app.callback(
    Output(component_id='status-graph',component_property='figure'),
    Input(component_id='color-output',component_property='children'),
    State(component_id='color-piker',component_property='value'),
    State(component_id='adjustment-selector',component_property='value'),
    State(component_id='range-slider',component_property='value')
)


def update_color(selected_leds,color_value,adjustment_selection,frequency_value):


    select_leds_list = literal_eval(selected_leds) # Turn the selected string to a list
    
    # print(select_leds_list)
    
    print(adjustment_selection)
    if adjustment_selection == "Adjust Color":
        print(color_value["hex"])
        df.loc[select_leds_list,'color'] = color_value["hex"]
    if adjustment_selection == "Adjust Frequency":
        df.loc[select_leds_list,'led_frequency'] = frequency_value
    
    # Send the data to dataframe

    fig = update_dataframe(df)
    fig.update_layout(transition_duration=500)
    send_to_uc(df)

    return fig



if __name__ == '__main__':
    app.run_server(debug=True,port=8000, host='0.0.0.0')
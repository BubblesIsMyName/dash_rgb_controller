# install dash / plotly / pandas / dash_daq
# !pip install dash jupyter-dash pandas

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#%% IMPORT

import http
import string
from dash import Dash, html, dcc, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_daq as daq
from copy import copy
from ast import literal_eval
import serial # for sending to the Arduino
from PIL import ImageColor # For converting from hex to RGB
import time # For a short puase at the startup

ser = serial.Serial("/dev/ttyUSB1")
app = Dash(__name__)

#%% LOAD DATAFRAME

path_to_saved_df = "./last_df.csv"
led_strip_size = 46 # size of the led strip

def save_df():
    df.to_csv(path_or_buf=path_to_saved_df)
def load_df():
    return pd.read_csv(path_to_saved_df,low_memory=False,index_col=0)


def start_dataframe():
    '''
     Create the dataframe, that will be used for informing led behavior
    '''
    try:
        df = load_df()
        print("loaded the dataframe on the startup")
        time.sleep(3)
        send_to_uc(df)
    except:
        df = pd.DataFrame()
        # df["led_brightness"] = np.random.randint(1,10,size = led_strip_size).tolist() # For random initial frequencies

        colors_list = [   # Initial color list
        '#D7537F',
        '#53D764',
        '#D1D753',
        '#D75853',
        '#53A0D7'
        ]

        df["color"] = np.random.choice(colors_list,led_strip_size)
        df["led_brightness"] = 10
    return df

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

def hex_to_avg(hex_str:str):
    return np.mean(ImageColor.getcolor(hex_str,"RGB"))

def update_dataframe(df):

    # column with copy of the frequncy values as strings, to make them discrete
    df["led_index_str"] = df.index
    df["led_index_str"] = df["led_index_str"].apply(lambda x:str(x)) 
    df["rgb"] = df["color"].apply(hex_to_rgb)
    # Get the sudo brightness level average of the the 3 rgb values
    df["led_brightness"] = df.color.apply(hex_to_avg)
    # Create a dsicrete color map
    list_of_values = df.color.to_list()
    color_map = {str(item):(list_of_values[item]) for item in range(len(list_of_values))}
    # print(color_map)



    fig = px.scatter(df,
                    x=df.index,
                    y="led_brightness",
                    color="led_index_str",
                    color_discrete_map=color_map,
                    
                    size = "led_brightness",

                    labels = {
                        "led_brightness":"Brightness",
                        "index":"LED number, total of {}".format(led_strip_size)
                        }
                    )

    fig.update_layout(
                    showlegend=False,
                    # clickmode
                    dragmode = 'select' # uses the box selector by default
                    )
    return fig

df = start_dataframe()

def update_existing_df():
    global df 
    df = pd.read_csv(path_to_saved_df,low_memory=False,index_col=0)

fig = update_dataframe(df)



app.layout = html.Div(children=[

    dcc.Graph(
        id='status-graph',
        figure=fig
    ),

    html.Div(id = 'color-output'),

    daq.ColorPicker(
        id = 'color-piker',
        value=dict(hex='#119DFF'),
        size = 800
    ),
    
    # saving and loading the colors
    html.Button("Save", id="save-button"),
    html.Button("Load", id="load-button"),
    html.Div(id ='status-prompt')



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
    Input(component_id='status-prompt',component_property='children'),
    State(component_id='color-piker',component_property='value'),
)


def update_color(selected_leds,load_status,color_value):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print(changed_id)
    
    if select_leds == "Nothing Selected":
        print("No Led's selected (update color)")
    elif "load-button" in changed_id:
        print("No Led's selected (update color) loaded previous")
    else:
        select_leds_list = literal_eval(selected_leds) # Turn the selected string to a list
        print(color_value["hex"])
        df.loc[select_leds_list,'color'] = color_value["hex"]
    
    # Send the data to dataframe
    fig = update_dataframe(df)
    fig.update_layout(transition_duration=500)

    send_to_uc(df)

    return fig

# !!!!!!  Load and save the colors to a dataframe
@app.callback(
    Output(component_id='status-prompt',component_property='children'),
    Input(component_id='save-button',component_property='n_clicks'),
    Input(component_id='load-button',component_property='n_clicks')
)

def update_stored_datafrme(save_click,load_click):

    status_string = "Status: nothing_done"
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if "save-button" in changed_id:
        try:
            print("saving the df")
            save_df()
            status_string = "Saved dataframe"
        except Exception as e:
            print(e)
    if "load-button" in changed_id:
        try:
            print("loading the df")
            update_existing_df()
            print(df)
            status_string = "Loaded dataframe"
        except Exception as e:
            print(e)
    
    print(status_string)
    return status_string
    

if __name__ == '__main__':
    app.run_server(debug=True,port=8000, host='0.0.0.0')
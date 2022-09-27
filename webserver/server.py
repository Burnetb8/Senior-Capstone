from dash import Dash, html, Input, Output
import dash_daq as daq
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import pandas as pd

app = Dash(__name__)

coords = [29.1802, -81.0598]

location_map = folium.Map(location=coords, zoom_start=13)
location_map.save("map.html")

app.layout = html.Div(children=[
    html.H1(children='ATC Map'),

    daq.ToggleSwitch(
        id='map-switch',
        label="Toggle Map",
        value=False
    ),

    html.Div(id='map', children=[
        html.Iframe(id='physical_map', srcDoc=open("map.html","r").read(), width="100%", height="500"),

        # Hidden by default 
        html.Img(id='airplane_map', className="hidden", src=app.get_asset_url('Screenshot_20220909-140804.png'), style={"width": "100%"})
    ])
])

# Toggle the "hidden" class name for the physical and airplane maps 
@app.callback(
    [Output('physical_map', 'className'), Output('airplane_map', 'className')],
    [Input('map-switch', 'value')]
)
def update_output(value):
    physical_map_classname = "hidden" if value else ""
    airplane_map_classname = "" if value else "hidden"
    return physical_map_classname, airplane_map_classname

if __name__ == '__main__':
    app.run_server(debug=True)


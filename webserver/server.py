from dash import Dash, html, Input, Output
import dash_daq as daq
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import pandas as pd

app = Dash(
    __name__,
    title='ATC Map',
)
app.scripts.config.serve_locally = False

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
        html.Iframe(id='interactive_map', srcDoc=open("map.html","r").read(), width="100%", height="500"),

        # Hidden by default 
        html.Img(id='image_map', className="hidden", src=app.get_asset_url('Jacksonville SEC.png'), style={"width": "100%"})
    ])
])

# Toggle the "hidden" class name for the interactive and image maps 
@app.callback(
    [Output('interactive_map', 'className'), Output('image_map', 'className')],
    [Input('map-switch', 'value')]
)
def update_output(value):
    interactive_map_classname = "hidden" if value else ""
    image_map_classname = "" if value else "hidden"
    return interactive_map_classname, image_map_classname

if __name__ == '__main__':
    app.run_server(debug=True)


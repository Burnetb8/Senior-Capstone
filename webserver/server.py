from dash import Dash, html, Input, Output, dcc
import dash_daq as daq
import dash_leaflet as dl
from opensky_fetching import fetch_opensky

lat_min = -85.0
lat_max = -80.0
lon_min = 28.0
lon_max = 33.0
lat_start = -81.0598
lon_start = 29.1802

opensky_info = fetch_opensky(lon_min, lon_max, lat_min, lat_max)

external_stylesheets = [{
    'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
    'rel': 'stylesheet',
    'crossorigin': 'anonymous'
}]

# Website settings
app = Dash(
    __name__,
    title='ATC Map',
    external_stylesheets=external_stylesheets
)

def mark_plane(lat, long, name, angle):
    return dl.DivMarker(
        iconOptions={
            'html': f'<i class="plane fa fa-plane" style="transform: rotate({angle}deg);color: white;font-size: 25px;text-shadow: 0 0 3px #000;">',
            'className': ''
        },
        position=(lat, long),
        title=name
    )

# Renders the map into a file
# Shown by default
def create_interactive_map(planes):
    return dl.Map([
            dl.TileLayer(),
            planes
        ],
        id='interactive_map',
        zoom=13,
        center=(lon_start, lat_start),
        style={'width': '100%', 'height': '90vh', 'z-index': '1'}
    )

# Mark all planes on interactive map
# import threading

def generate_planes():
    # threading.Timer(15.0, generate_planes).start()
    # print("HELLOOOOOO")
    markers = [mark_plane(
        lat=plane.latitude,
        long=plane.longitude,
        name=plane.callsign,
        angle=plane.true_track
    ) for plane in opensky_info]

    return dl.MarkerClusterGroup(
        id="markers",
        children=markers,
        options={'disableClusteringAtZoom': True}
    )

# Create the two maps
planes = generate_planes()
interactive_map = create_interactive_map(planes)
map_style = {'width': '100%', 'height': '90vh'}

# Render the layout of the website
app.layout = html.Div(children=[
    html.H1(children='ATC Map'),

    # Toggle map button
    daq.ToggleSwitch(
        id='map-switch',
        label="Toggle Map",
        value=False
    ),

    html.Div(
        id="popup",
        children=[
            html.P("test")
        ],
        draggable="true"
    ),

    html.Div(className="fas fa-plane plane"),

    html.Div(id='map', children=[
        # Interactive map
        interactive_map,

        # Image map
        html.Div(id='image_map', style=map_style)
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
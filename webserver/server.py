import json
from dash import Dash, html, Input, Output, dcc, ALL, MATCH, callback_context, exceptions
import dash_daq as daq
import dash_leaflet as dl
from opensky_fetching import fetch_opensky
from datetime import datetime
import pytz

lat_min = -85.0
lat_max = -80.0
lon_min = 28.0
lon_max = 33.0
lat_start = -81.0598
lon_start = 29.1802

all_planes_info = {}
selected_plane = None

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
            'html': f'<i class="plane fa fa-plane" style="transform: rotate({angle-45}deg);color: white;font-size: 25px;text-shadow: 0 0 3px #000;">', # Angle - 45 to account for the font awesome icon pointing 45 degrees northeast at 0 degrees rotation
            'className': ''
        },
        position=(lat, long),
        title=name,
        id={
            'type': 'plane',
            'index': name
        }
    )

# Renders the map into a file
# Shown by default
def create_interactive_map():
    return dl.Map([
            dl.TileLayer(),
            dl.MarkerClusterGroup(
                id="plane-markers",
                children=[],
                options={'disableClusteringAtZoom': True}
            )
        ],
        id='interactive_map',
        zoom=13,
        center=(lon_start, lat_start),
        style={'width': '100%', 'height': '90vh', 'zIndex': '1'}
    )

# Mark all planes on interactive map
def generate_planes():
    global all_planes_info
    all_planes_info = {plane.callsign: plane for plane in fetch_opensky(lon_min, lon_max, lat_min, lat_max)}
    return [mark_plane(
        lat=all_planes_info[plane_name].latitude,
        long=all_planes_info[plane_name].longitude,
        name=all_planes_info[plane_name].callsign,
        angle=all_planes_info[plane_name].true_track
    ) for plane_name in all_planes_info]

# Create the two maps
interactive_map = create_interactive_map()
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
        html.Div(id='image_map', style=map_style),

        dcc.Interval(
            id='map-refresh',
            interval=15*1000 # 15 seconds 
        )
    ])
])

def generate_popup_text(this_plane):
    return [
        f"Callsign: {this_plane.callsign}",
        f"Origin: {this_plane.origin_country}",
        f"Last Contact: {datetime.fromtimestamp(this_plane.last_contact, tz=pytz.timezone('America/New_York')).strftime('%m/%d/%Y %H:%M %Z')}",
        f"Location: ({this_plane.latitude}\u00B0, {this_plane.longitude}\u00B0)",
        f"Altitude: {this_plane.geo_altitude}m",
        f"Velocity: {this_plane.velocity} m/s",
        f"Track: {this_plane.true_track}\u00B0",
        f"Vertical Rate: {this_plane.vertical_rate} m/s",
        f"Squawk: {this_plane.squawk}",
    ]

# Toggle the "hidden" class name for the interactive and image maps 
@app.callback(
    [Output('interactive_map', 'className'), Output('image_map', 'className')],
    [Input('map-switch', 'value')]
)
def update_output(value):
    interactive_map_classname = "hidden" if value else ""
    image_map_classname = "" if value else "hidden"
    return interactive_map_classname, image_map_classname

@app.callback(Output('plane-markers', 'children'),
              Input('map-refresh', 'n_intervals'))
def update_map(n):
    p = generate_planes()
    return p

# Onclick plane icon
@app.callback(
    Output('popup', 'children'),
    Input({'type': 'plane', 'index': ALL}, 'n_clicks')
)
def plane_click(n_clicks):
    global selected_plane

    if 'index' in callback_context.triggered[0]['prop_id']:
        selected_plane = json.loads(callback_context.triggered[0]['prop_id'][0:-9])['index']

        #TODO prevent initial page load populating popup with index 0's info
        #TODO Keep the same selected_plane each time map updates

        if selected_plane == None:
            raise exceptions.PreventUpdate

        this_plane = all_planes_info[selected_plane]

        return html.Div(children=[html.Span([item, html.Br()]) for item in generate_popup_text(this_plane)])
    else:
        raise exceptions.PreventUpdate
    

# Reset n_clicks attribute for each plane icon, so it can be clicked again
@app.callback(
    Output({'type': 'plane', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'plane', 'index': MATCH}, 'n_clicks')
)
def upon_click(n_clicks):
    if (n_clicks is None): raise exceptions.PreventUpdate
    return None

if __name__ == '__main__':
    app.run_server(debug=True)
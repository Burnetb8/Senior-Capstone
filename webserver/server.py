import json
from dash import Dash, html, Input, Output, dcc, MATCH, callback_context
import dash
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
aeronautical_coords = {
    'lon_min': -175.2,
    'lon_max': -134,
    'lat_min': 81.47,
    'lat_max': 85,
    'lon_start': -150.28857327997687,
    'lat_start': 82.71605972541532
}

active_map = 0 # 0 = google map, 1 = aeronautical chart
all_planes_info = {}
selected_plane = None

external_stylesheets = [{
    'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
    'rel': 'stylesheet',
    'crossorigin': 'anonymous'
}]

# https://gamedev.stackexchange.com/a/32556
def scale_coords(x, src_min, src_max, dest_min, dest_max):
    return ( x - src_min ) / ( src_max - src_min ) * ( dest_max - dest_min ) + dest_min

def scale_lat(x):
    global active_map

    # Only scale coords if on aeronautical chart
    if active_map == 1:
        return scale_coords(x, 28, 32.25, aeronautical_coords['lat_min'], aeronautical_coords['lat_max'])
    else:
        return x

def scale_lon(x):
    global active_map

    # Only scale coords if on aeronautical chart
    if active_map == 1:
        return scale_coords(x, -85, -78.5, aeronautical_coords['lon_min'], aeronautical_coords['lon_max'])
    else:
        return x

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

def create_plane_marker_container():
    return dl.MarkerClusterGroup(
        id="plane-markers",
        children=[],
        options={'disableClusteringAtZoom': True}
    )

def create_map_scale():
    return dl.ScaleControl(metric=False)

# Renders the map into a file
# Shown by default
def create_interactive_map():
    return dl.Map(
        children=[
            dl.TileLayer(),
            create_map_scale(),
            create_plane_marker_container()
        ],
        id='interactive_map',
        zoom=13,
        center=(lon_start, lat_start),
        style={'width': '100%', 'height': '90vh', 'zIndex': '1'}
    )

def create_chart_tilelayer():
    return dl.TileLayer(
        url="/assets/output_files/{z}/{x}_{y}.jpeg",
        noWrap=True,
        tileSize=200,
        zoomOffset=6
    )

def create_image_map():
    return dl.Map(
    children=[create_chart_tilelayer()],
    zoom=8,
    maxZoom=9,
    minZoom=4,
    maxBounds=[[aeronautical_coords['lat_min'], aeronautical_coords['lon_min']], [aeronautical_coords['lat_max'], aeronautical_coords['lon_max']]],
    center=[aeronautical_coords['lat_start'], aeronautical_coords['lon_start']],
    style={'width': '100%', 'height': '90vh', 'zIndex': '1'},
    id='image_map'
    )

# Mark all planes on interactive map
def generate_planes():
    global all_planes_info
    new_planes_info = fetch_opensky(lon_min, lon_max, lat_min, lat_max)

    # Only update planes if there are planes to update, otherwise do nothing. This caches the planes if nothing is found
    if new_planes_info:
        all_planes_info = {plane.callsign: plane for plane in new_planes_info}

    return [mark_plane(
        lat=scale_lat(all_planes_info[plane_name].latitude),
        long=scale_lon(all_planes_info[plane_name].longitude),
        name=all_planes_info[plane_name].callsign,
        angle=all_planes_info[plane_name].true_track
    ) for plane_name in all_planes_info]

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
        create_interactive_map(),

        # Image map
        create_image_map(),

        dcc.Interval(
            id='map-refresh',
            interval=15*1000 # 15 seconds 
        ),

        dcc.Interval(
            id='popup-refresh',
            interval=500 # 0.5 seconds 
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

# Handler for when the toggle button is clicked
@app.callback(
    [Output('interactive_map', 'children'), Output('image_map', 'children'), Output('interactive_map', 'className'), Output('image_map', 'className')],
    [Input('map-switch', 'value')]
)
def update_output(value):
    global active_map
    active_map = 0 if not value else 1

    interactive_map_classname = "hidden" if value else ""
    image_map_classname = "" if value else "hidden"

    if value:
        # Toggle button activated: Image map
        # Toggle class and rewrite children for map
        return (
            [dl.TileLayer(),
            create_map_scale()],
            [create_chart_tilelayer(),
            create_map_scale(),
            create_plane_marker_container()],
            interactive_map_classname,
            image_map_classname
        )
    else:
        # Toggle button not activated: Interactive map
        # Toggle class and rewrite children for map
        return (
            [dl.TileLayer(),
            create_map_scale(),
            create_plane_marker_container()],
            [create_chart_tilelayer(),
            create_map_scale()],
            interactive_map_classname,
            image_map_classname
        )

# Update the plane markers at interval
@app.callback(Output('plane-markers', 'children'),
                Input('map-refresh', 'n_intervals'))
def update_map(n):
    p = generate_planes()
    return p

# Refresh the popup text at interval
@app.callback(Output('popup', 'children'),
              Input('popup-refresh', 'n_intervals'),
            prevent_initial_call=True)
def popup_refresh(n):
    if selected_plane and selected_plane in all_planes_info:
        return html.Div(children=[html.Span([item, html.Br()]) for item in generate_popup_text(all_planes_info[selected_plane])])

# Update the selected plane on click 
@app.callback(
    Output({'type': 'plane', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'plane', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def plane_click(n_clicks):
    global selected_plane
    selected_plane = json.loads(callback_context.triggered[0]['prop_id'][0:-9])['index']
    return None

if __name__ == '__main__':
    app.run_server(debug=True)
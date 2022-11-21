from dash import Dash, html, Input, Output, dcc
import dash_daq as daq
import folium

external_stylesheets = [{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

# Website settings
app = Dash(
    __name__,
    title='ATC Map',
    external_stylesheets=external_stylesheets
)

def mark_plane(folium_map, lat, long):
    folium.Marker(
        location=[lat, long],
        popup='<div id="popup">Testing testing</div>',
    ).add_to(folium_map)
    folium_map.save("map.html")

# Renders the map into a file
# Shown by default
def create_interactive_map():
    coords = [29.1802, -81.0598]

    location_map = folium.Map(location=coords, zoom_start=13)
    location_map.save("map.html")
    return location_map

# Create the two maps
interactive_map = create_interactive_map()
map_style = {'width': '100%', 'height': '90vh'}

mark_plane(interactive_map, 29.0613, -80.9146)

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
        html.Iframe(id='interactive_map', srcDoc=open("map.html","r").read(), style=map_style),

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
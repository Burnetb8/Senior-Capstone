from dash import Dash, html, Input, Output, dcc
from dash.dependencies import State
import dash_daq as daq
import plotly.express as px
import folium
import PIL
from PIL import Image
import numpy

external_stylesheets = [{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

PIL.Image.MAX_IMAGE_PIXELS = 933120000 # Allow pillow to load large files (like our tif file)

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

# Returns the map in ram
# Hidden by default
def create_image_map(x1=8000, x2=13000, y1=6500, y2=8500):
    file = 'assets/Jacksonville SEC.tif'

    im = Image.open(file) # Open tif
    imarray = numpy.array(im) # Convert to numpy array
    cropped_array = imarray[int(y1):int(y2), int(x1):int(x2)] # Crop: height1:height2, width1:width2

    fig = px.imshow(cropped_array,binary_string=True)

    # Enable panning ability, remove white margins around the whole map, set width to 100%
    fig.update_layout(dragmode="pan", margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0   
    ),
    autosize=True)

    # Remove the ugly numbers 
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Graph options 
    config = {
        'displaylogo': False
    }

    return {
        'fig': fig,
        'config': config
    }

# Create the two maps
interactive_map = create_interactive_map()
image_map = create_image_map()
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
        dcc.Graph(id='image_map', figure=image_map['fig'], config=image_map['config'], style=map_style),
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

@app.callback(
    Output('image_map', 'figure'),
    Input('image_map', 'relayoutData'),
    State('image_map', 'figure'))
def display_relayout_data(relayoutData,figure):
    print(relayoutData)

    if relayoutData and 'xaxis.range[0]' in relayoutData:
        return create_image_map(x1=relayoutData['xaxis.range[0]']+8000.5, x2=relayoutData['xaxis.range[1]']+8000.5, y1=relayoutData['yaxis.range[1]']+6500.5, y2=relayoutData['yaxis.range[0]']+6500.5)['fig']
    else:
        return figure

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_leaflet as dl
import numpy as np

app = dash.Dash(__name__)
app.layout = dl.Map([dl.TileLayer(
                                url="/assets/output_files/{z}/{x}_{y}.png",
        noWrap=True,
        tileSize=512,
        zoomOffset=10,
        
        # zoomOffset=17,
        # bounds=[{'lat': 0, 'lon': 12412}, {'lat': 16617, 'lon': 0}]
        # bounds=[[5    7, 11], [58, 12]],
        # bounds=np.asarray([12412,16617])

        # bounds=[0,0]
                            ),
                            dl.MarkerClusterGroup(id="markers", children=[dl.Marker(
                title='test',
                position=(0,0),
                # icon='plane'
            )])],
        zoom=4,
        maxZoom=5,
        bounds=[[0,24], [32,0]],
        center=[0,0],
        style={'height': '100vh'})

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)

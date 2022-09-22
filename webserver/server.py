from dash import Dash, html, dcc
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

    html.Button(id='switch', children='Switch Map'),

    # dcc.Graph(
    #     id='example-graph',
    #     figure=fig
    # )

    html.Iframe(srcDoc=open("map.html","r").read(), width="100%", height="500")
])

if __name__ == '__main__':
    app.run_server(debug=True)


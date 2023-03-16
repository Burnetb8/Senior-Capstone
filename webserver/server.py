from dash import Dash, html, Input, Output
import dash
import dash_daq as daq

external_stylesheets = [{
    'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
    'rel': 'stylesheet',
    'crossorigin': 'anonymous'
}]

# Website settings
app = Dash(
    __name__,
    title='ATC Map',
    external_stylesheets=external_stylesheets,
    use_pages=True
)

map_types = ["Interactive Map", "Aeronautical Chart Map"]

def create_toggle_label(map):
    return f"Click to view {map_types[map]}"

header = html.Header(className="foreground w10 wrapper-horizontal", children=[
    html.Div(className="w5 center left wrapper-horizontal", children=[
        html.A(href='/', children=[
            html.H2(children='ATC Map', className="link")
        ]),
        html.A(href="/about", children="About", className="link")
    ]),

    html.Div(className="w5 center right", children=[
        # Toggle map button
        daq.ToggleSwitch(
            id='map-switch',
            label=create_toggle_label(0),
            value=False,
            size=45,
            color='#2c62c6',
            labelPosition='bottom',
            className='link'
        )
    ])
])

# Render the layout of the website
app.layout = html.Div(children=[
    header,

    dash.page_container # Content of each page
])

# TODO FIX ME!!! Toggle text doesn't change on click 
# @app.callback(
#     [Output('map-switch', 'label')],
#     [Input('map-switch', 'value')]
# )
# def toggle_switch(value):
#     other_map = 0 if value else 1
#     return create_toggle_label(other_map)


if __name__ == '__main__':
    app.run_server(debug=True)
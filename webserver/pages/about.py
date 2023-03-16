import dash
from dash import html

dash.register_page(__name__, path='/about')

layout = html.Div(children=[
    html.Div(className="wrapper-vertical w10 center", children=[
        html.Div(className="wrapper-horizontal w9 p3 center alt-left", children=[
            html.Div(className="w5", children=[
                html.Div(className="foreground card", children=[
                    html.Div(className="p3 margin-below", children=[
                        html.H3(children="About"),
                        html.P("Blah blah description here")
                    ])
                ])
            ]),
            html.Div(className="w5", children=[
                html.Div(className="foreground card", children=[
                    html.Div(className="p3 margin-below", children=[
                        html.H3(children="Links"),
                        html.Ul(children=[
                            html.Li(children=[
                                html.A(href="https://github.com/Burnetb8/Senior-Capstone", target="_blank", children="GitHub Repository"),
                            ]),
                            html.Li(children=[
                                html.A(href="https://trello.com/b/zKXAUiNI/scrum-board-spring", target="_blank", children="Trello Board")
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
])
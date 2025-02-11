# footer.py
from dash import html
import dash_bootstrap_components as dbc

class Footer:
    @staticmethod
    def create(counter):
        """Creates the footer component with credits and counter."""
        return dbc.Container([
            dbc.Row([
                html.Footer(
                    className="mt-5",
                    style={
                        'width': '100%',
                        'backgroundColor': '#f8f9fa',
                        'borderTop': '1px solid #dee2e6',
                        'padding': '2rem 0',
                    },
                    children=[
                        dbc.Container(
                            fluid=True,
                            style={'maxWidth': '100%', 'paddingLeft': '0', 'paddingRight': '0'},
                            children=[
                                # Container for title and counter
                                html.Div(
                                    style={'position': 'relative'},
                                    children=[
                                        # Centered title
                                        html.Div(
                                            html.H4("By Dani & Dati", className="mb-3"),
                                            className="text-center"
                                        ),
                                        # Absolutely positioned counter
                                        html.Div(
                                            counter.get_counter_component(),
                                            style={
                                                'position': 'absolute',
                                                'right': '20px',
                                                'top': '0'
                                            }
                                        )
                                    ]
                                ),

                                # Rest of the content
                                html.Div(
                                    className="text-center",
                                    style={'marginLeft': 'auto', 'marginRight': 'auto', 'maxWidth': '1200px'},
                                    children=[
                                        html.Div([
                                            html.H5("Contributors", className="mt-4"),
                                            html.Ul([
                                                html.Li("Koki - Server Backend"),
                                                html.Li("Marco Zeuli - Developer"),
                                                html.Li("Matteo Veroni - Developer"),
                                            ], className="list-unstyled text-muted"),
                                        ], className="col-md-4 mx-auto"),

                                        html.Div(
                                            [
                                                html.A("Contribuisci allo sviluppo",
                                                      href="https://github.com/daniele96l/backtester-dani",
                                                      style={'textDecoration': 'none'})
                                            ],
                                            style={'color': 'gray', 'marginTop': '1rem'}
                                        ),
                                        html.A(
                                            "Informativa sulla privacy",
                                            href="https://danieleligato-eng.notion.site/Informativa-sulla-privacy-197922846a1680d5bc0fc50711843137",
                                            target="_blank",
                                            className="d-block text-primary mb-3",
                                            style={"text-decoration": "none"},
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                )
            ], className='mt-5'),
        ], fluid=True)
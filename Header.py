# header.py
from dash import html
import dash_bootstrap_components as dbc

class Header:
    @staticmethod
    def create():
        """Creates the header component with logo and user indicator."""
        login_indicator = html.Div(
            "👤",
            id="login-indicator",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "fontSize": "24px",
                "zIndex": 1500,
                "cursor": "default",
                "transition": "opacity 0.3s ease"
            }
        )

        header = dbc.Container([
            login_indicator,
            dbc.Row(
                dbc.Col(
                    html.Img(
                        src="/assets/newlogo.png",
                        className="responsive-logo",
                        style={
                            'maxHeight': '50px',
                            'margin': 'auto',
                            'display': 'block',
                            'transition': 'all 0.3s ease-in-out'
                        }
                    ),
                    width=12
                ),
                className='mb-4',
                style={
                    'backgroundColor': '#F8F9FA',
                    'padding': '20px 20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }
            ),
        ], fluid=True)

        return header
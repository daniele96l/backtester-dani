# layout.py
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash.dash_table
from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, DEV_FIVE_FACTORS_FILE_PATH, INDEX_LIST_FILE_PATH, ETF_BASE_PATH
from Popup import PopupManager
class LayoutManager:
    @staticmethod
    def create_layout(asset_list, initial_table_data,app):


        modal = PopupManager(app)
        """Definisce il layout dell'app Dash utilizzando componenti Bootstrap."""
        return html.Div([
            # Header Container - Occupa tutta la larghezza dello schermo
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        html.Img(
                            src="/assets/Logo2.png",  # Path to the logo in the assets folder
                            style={
                                'maxHeight': '100px',  # Set max height for the logo
                                'margin': 'auto',  # Center the logo
                                'display': 'block'
                            }
                        ),
                        width=12
                    ),
                    className='mb-4',  # Aggiunge un margine inferiore di 1.5rem
                    style={
                        'backgroundColor': '#F8F9FA',  # Grigio chiaro
                        'padding': '20px 20px',  # Padding verticale
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'  # Ombra leggera per profondità
                    }
                ),
            ], fluid=True),  # Container fluido per estendere l'header su tutta la larghezza

            # Main Content Container - Con margini orizzontali
            dbc.Container([
                # Riga di Selezione: Dropdown ETF e Slider Percentuale
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Seleziona un ETF (Nome, ISIN, Ticker):", style={'color': '#000000'}),
                        dcc.Dropdown(
                            id='etf-dropdown',
                            options=asset_list,
                            placeholder="Seleziona un ETF",
                            className='mb-3',
                            style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                        )
                    ], md=6),

                    dbc.Col([
                        dbc.Label("Percentuale di Allocazione:", style={'color': '#000000'}),
                        dbc.Input(
                            id='percentage-input',
                            type='number',
                            min=0.1,
                            value=100,
                            style={'width': '100%'},
                        )
                    ], md=6),
                ], className='mb-4'),

                # Pulsante Aggiungi ETF
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            "Aggiungi ETF",
                            id='add-etf-button',
                            color='danger',
                            className='w-100',
                            style={
                                'backgroundColor': '#FA8072',
                                'borderColor': '#FA8072',
                                'minWidth': '100px',  # Minimum width
                                'minHeight': '40px'  # Minimum height
                            }
                        ),
                        width=2
                    ),
                    className='mb-4'
                ),

                # Tabella del Portafoglio
                dbc.Row(
                    dbc.Col(
                        dash.dash_table.DataTable(
                            id='portfolio-table',
                            columns=[
                                {"name": "ETF", "id": "ETF", "editable": False},
                                {"name": "Percentuale (%)", "id": "Percentuale", "editable": True, 'type': 'numeric',
                                 'format': {'specifier': '.2f'}},
                            ],
                            data=initial_table_data.to_dict('records'),  # Ensure your data includes "Inizio storia"
                            editable=True,
                            row_deletable=True,
                            style_table={'width': '100%', 'overflowX': 'auto', 'backgroundColor': '#FFFFFF'},
                            style_cell={'textAlign': 'left', 'padding': '10px', 'color': '#000000'},
                            style_header={
                                'backgroundColor': '#F0F0F0',
                                'fontWeight': 'bold',
                                'color': '#000000'
                            },
                            style_as_list_view=True,
                        ),
                        width=12
                    ),
                    className='mb-4'
                ),

                dbc.Row([
                    # Colonna per il pulsante
                    dbc.Col(
                        dbc.Button("Crea/Aggiorna Portafoglio", id='create-portfolio-button', color='danger',
                                   className='w-100 mt-4',
                                   style={'backgroundColor': '#8B4513', 'borderColor': '#8B4513'}),
                        md=2,  # Specifica la larghezza della colonna
                    ),
                    # Colonna per il dropdown
                    dbc.Col([
                        dbc.Label("Scegli il tuo Benchmark (Opzionale):", style={'color': '#000000'}),
                        dcc.Dropdown(
                            id='benchmark-dropdown',
                            options=asset_list,
                            placeholder="Seleziona un Benchmark",
                            className='mb-3',
                            style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                        )
                    ], md=6),  # Specifica la larghezza della colonna
                    #  per la selezione degli anni
                    dbc.Col([
                        dbc.Label("Anno Inizio (Opzionale):", style={'color': '#000000'}),
                        dcc.Dropdown(
                            id='start-year-dropdown',
                            options=[{'label': str(year), 'value': year} for year in range(1990, 2025)],
                            placeholder="Seleziona Anno Inizio",
                            className='mb-3',
                            style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                        )
                    ], md=2),  # Specifica la larghezza della colonna per Anno Inizio

                    dbc.Col([
                        dbc.Label("Anno Fine (Opzionale):", style={'color': '#000000'}),
                        dcc.Dropdown(
                            id='end-year-dropdown',
                            options=[{'label': str(year), 'value': year} for year in range(1990, 2025)],
                            placeholder="Seleziona Anno Fine",
                            className='mb-3',
                            style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                        )
                    ], md=2)  # Specifica la larghezza della colonna per Anno Fine
                ], className='mt-5'),

                # Sommario Allocazione e Feedback
                dbc.Row([
                    dbc.Col(
                        html.Div(id='allocation-summary', className='mt-4 text-center',
                                 style={'fontSize': '1.1em', 'color': '#000000'}),
                        width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        html.Div(id='portfolio-feedback', className='mt-2 text-center',
                                 style={'fontSize': '1.1em', 'color': '#8B4513'}),
                        width=12
                    )
                ]),
                dcc.Store(id='portfolio-data', storage_type='memory'),  # Aggiungi questo componente
                dcc.Store(id='assets-data', storage_type='memory'),  # Aggiungi questo componente
                dcc.Store(id='pesi-correnti', storage_type='memory'),
                dbc.Toast(
                    id="allocation-error-toast",
                    header="Stai superando il 100% di allocazione del tuo portafoglio, rimuovi o modifica le percentuali.",
                    dismissable=True,
                    duration=3000,  # Durata in millisecondi (2 secondi)
                    is_open=False,  # Nascondi inizialmente
                    style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000},  # Posizionamento
                ),
                dbc.Toast(
                    id="Work-in-progress-toast",
                    header="Funzione in sviluppo, Arriverà presto!",
                    dismissable=True,
                    duration=3000,  # Durata in millisecondi (2 secondi)
                    is_open=False,  # Nascondi inizialmente
                    style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000},  # Posizionamento
                ),

                dbc.Toast(
                    [
                        html.Div([
                            html.P("🤖", style={"fontSize": "60px", "marginBottom": "10px"}),  # Emoji robot grande
                            html.P("Calcolo con algoritmi universitari...",
                                   style={"margin": "0", "fontSize": "22px", "fontWeight": "bold"})
                        ], style={"textAlign": "center"})
                    ],
                    id="portfolio-toast",
                    dismissable=False,  # Non chiudibile manualmente
                    duration=3000,  #
                    is_open=False,
                    style={
                        "position": "fixed",
                        "top": "50%",  # Centrare verticalmente
                        "left": "50%",  # Centrare orizzontalmente
                        "transform": "translate(-50%, -50%)",  # Perfetto centramento
                        "zIndex": 1500,  # In primo piano rispetto agli altri elementi
                        "backgroundColor": "rgba(0, 0, 0, 0.8)",  # Sfondo scuro trasparente
                        "color": "#ffffff",  # Testo bianco
                        "padding": "30px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",  # Aggiunge un'ombra leggera
                    },
                ),

                # Div per Feedback Aggiuntivo
                dbc.Row([
                    dbc.Col(
                        html.Div(id='additional-feedback', className='mt-2 text-center',
                                 style={'fontSize': '1.1em', 'color': '#0000FF'}),  # Colore blu per esempio
                        width=12
                    )
                ]),
                # Floating Button
                dbc.Button(
                    children="Tutorial",  # Text on the button
                    id="tutorial-button",
                    style={
                        "backgroundColor": PORTFOLIO_COLOR,  # Use the color variable
                        "color": "#000",  # Text color (adjust for contrast)

                    },
                    className="btn-floating",  # Use the CSS class defined in styles.css
                ),

                # Floating Button
                dbc.Button(
                    children="Donate",  # Text on the button
                    id="donate-button",
                    style={
                        "backgroundColor": PORTFOLIO_COLOR,  # Use the color variable
                        "color": "#000",  # Text color (adjust for contrast)

                    },
                    className="btn-donating",  # Use the CSS class defined in styles.css
                ),


                # Floating Button
                dbc.Button(
                    children="Account\n(Soon)",  # Text on the button
                    id="account-button",
                    style={
                        "backgroundColor": PORTFOLIO_COLOR,  # Use the color variable
                        "color": "#000",  # Text color (adjust for contrast)

                    },
                    className="btn-account",  # Use the CSS class defined in styles.css
                ),

                dbc.Button(
                    "Esporta il Report in PDF.",
                    id="save-pdf-button",
                    style={
                        "backgroundColor": PORTFOLIO_COLOR,  # Use the color variable
                        "color": "#000",  # Text color
                        "width": "100%",
                        "marginBottom": "50px",  # Add space below the button
                    },
                    className="mt-3",
                ),
                html.Div(id="hidden-div", style={"display": "none"}),

                dcc.Location(id="url", refresh=True),

            ], className='px-4', style={'backgroundColor': '#FFFFFF'}),

            modal,

            dbc.Container([
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
                                    html.Div(
                                        className="text-center",
                                        style={'marginLeft': 'auto', 'marginRight': 'auto', 'maxWidth': '1200px'},
                                        children=[
                                            # Contributors section
                                            html.Div([
                                                html.H4("By Dani & Dati", className="mb-3"),
                                                html.H5("Contributors", className="mt-4"),
                                                html.Ul([
                                                    html.Li("Koki - Server Backend"),
                                                    html.Li("Marco Zeuli - Developer"),
                                                    html.Li("Matteo Veroni - Developer"),
                                                ], className="list-unstyled text-muted"),
                                                # Making contributors appear less prominent
                                            ], className="col-md-4 mx-auto")
                                            ,

                                            # Link to contribute
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Se vuoi contribuire al progetto open source il codice è pubblico "),
                                                    html.A(
                                                        "QUI",
                                                        href="https://github.com/daniele96l/backtester-dani",
                                                        style={'color': 'gray', 'textDecoration': 'none'}
                                                    )
                                                ],
                                                style={'color': 'gray', 'marginTop': '1rem'}
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ],
                    )
                ], className='mt-5'),
            ], fluid=True)

        ])






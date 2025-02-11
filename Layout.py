# Layout.py
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash.dash_table
from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, DEV_FIVE_FACTORS_FILE_PATH, INDEX_LIST_FILE_PATH, ETF_BASE_PATH, COUNTER_FILE_PATH
from LoginPopout import PopupManager
from counter import PortfolioCounter

class LayoutManager:
    @staticmethod
    def create_layout(asset_list, initial_table_data,app):

        modal = PopupManager(app)
        counter = PortfolioCounter(COUNTER_FILE_PATH)
        counter.register_callbacks(app)
        # Emoji login indicator
        login_indicator = html.Div(
            "👤",  # Emoji utente
            id="login-indicator",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",  # Cambiato da "right" a "left"
                "fontSize": "24px",
                "zIndex": 1500,
                "cursor": "default",
                "transition": "opacity 0.3s ease"
            }
        )
        """Definisce il layout dell'app Dash utilizzando componenti Bootstrap."""
        return html.Div([
            dcc.Store(id='login-state', storage_type='local'),  # Login state available to all components
            #dcc.Location(id="url", refresh=True),
            login_indicator,  # Aggiungi l'indicatore emoji utente
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        html.Img(
                            src="/assets/newlogo.png",  # Path to the logo in the assets folder
                            style={
                                'maxHeight': '50px',  # Set max height for the logo
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
                    # ETF Dropdown
                    dbc.Col([
                        dbc.Label("Seleziona un ETF (Nome, ISIN, Ticker):", style={'color': '#000000'}),
                        html.Div([
                            dcc.Dropdown(
                                id='etf-dropdown',
                                options=asset_list,
                                placeholder="Seleziona un ETF",
                                className='modern-dropdown',
                                style={
                                    'backgroundColor': '#FFFFFF',
                                    'color': '#000000',
                                    'height': '40px'  # Altezza esplicita
                                }
                            ),
                            html.I(className="fas fa-chart-line dropdown-icon")
                        ], className="dropdown-container")
                    ], md=6),

                    # Percentuale
                    dbc.Col([
                        dbc.Label("Percentuale di Allocazione:", style={'color': '#000000'}),
                        dbc.Input(
                            id='percentage-input',
                            type='number',
                            min=0.1,
                            value=100,
                            style={
                                'width': '100%',
                                'height': '40px'  # Stessa altezza del dropdown
                            }
                        )
                    ], md=4),

                    # Bottone
                    dbc.Col([
                        dbc.Button(
                            "Aggiungi ETF",
                            id='add-etf-button',
                            color='danger',
                            style={
                                "height": "40px",  # Stessa altezza degli altri elementi
                                "margin-top": "32px",
                                "width": "100%",
                                "line-height": "40px",  # Per centrare il testo verticalmente
                                "padding": "0px"
                            }
                        ),
                    ], md=2, className="d-flex align-items-end"),
                ], className='mb-4'),

                # Tabella del Portafoglio
                dbc.Row([
                    dbc.Col([
                        # Table container with shadow and rounded corners
                        html.Div([
                            #Add a title
                            html.H5("Tabella Portafoglio", className="table-title"),
                            dash.dash_table.DataTable(
                                id='portfolio-table',
                                columns=[
                                    {"name": "ETF", "id": "ETF", "editable": False},
                                    {"name": "Percentuale (%)", "id": "Percentuale", "editable": True,
                                     'type': 'numeric',
                                     'format': {'specifier': '.2f'}},
                                ],
                                data=initial_table_data.to_dict('records'),
                                editable=True,
                                row_deletable=True,
                                style_table={
                                    'overflowX': 'auto',
                                },
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '16px',
                                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                },
                                style_header={
                                    'backgroundColor': '#f8f9fa',
                                    'fontWeight': '600',
                                    'borderBottom': '2px solid #dee2e6',
                                    'color': '#6c757d',
                                    'textTransform': 'uppercase',
                                    'fontSize': '0.75rem',
                                    'letterSpacing': '0.05em'
                                },
                                style_data={
                                    'color': '#212529',
                                    'backgroundColor': 'white',
                                    'fontSize': '0.875rem'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f8f9fa',
                                    }
                                ],
                            ),
                            # Percentage remaining card
                            html.Div(
                                id='remaining-percentage',
                                className='percentage-remaining-card'
                            )
                        ], className='table-container')
                    ], width=12)
                ], className='mb-4'),

                dbc.Row([
                    dbc.Col([
                        html.Div([


                            # Seconda riga: Periodo e Bottone affiancati
                            dbc.Row([
                                # Periodo di Analisi
                                dbc.Col([
                                    html.Label(
                                        "Periodo di Analisi (Opzionale)",
                                        className="settings-label"
                                    ),
                                    dbc.Row([
                                        # Start Year
                                        dbc.Col([
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='start-year-dropdown',
                                                    options=[{'label': str(year), 'value': year}
                                                             for year in range(1990, 2025)],
                                                    placeholder="Anno Inizio",
                                                    clearable=True,
                                                    className="modern-dropdown"
                                                ),
                                                html.I(className="far fa-calendar dropdown-icon")
                                            ], className="dropdown-container")
                                        ], width=6, className="pe-2"),

                                        # End Year
                                        dbc.Col([
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='end-year-dropdown',
                                                    options=[{'label': str(year), 'value': year}
                                                             for year in range(1990, 2025)],
                                                    placeholder="Anno Fine",
                                                    clearable=True,
                                                    className="modern-dropdown"
                                                ),
                                                html.I(className="far fa-calendar dropdown-icon")
                                            ], className="dropdown-container")
                                        ], width=6, className="ps-2"),
                                    ], className="g-0")
                                ], md=8),

                                # Create/Update Portfolio Button - allineato sulla stessa riga
                                dbc.Col([
                                    dbc.Button(
                                        [
                                            html.I(className="fas fa-sync-alt me-2"),
                                            "Crea/Aggiorna Portafoglio"
                                        ],
                                        color = 'danger',
                                        id='create-portfolio-button',
                                        style={
                                            "height": "40px",  # Stessa altezza degli altri elementi
                                            "margin-top": "32px",
                                            "width": "100%",
                                            "line-height": "40px",  # Per centrare il testo verticalmente
                                            "padding": "0px"
                                        }
                                    ),
                                ], md=4),
                            ], className="align-items-end"),

                            # Prima riga: Solo Benchmark
                            dbc.Row([
                                dbc.Col([
                                    html.Label(
                                        "Benchmark (Opzionale)",
                                        className="settings-label"
                                    ),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='benchmark-dropdown',
                                            options=asset_list,
                                            placeholder="Seleziona un benchmark",
                                            clearable=True,
                                            className="modern-dropdown"
                                        ),
                                        html.I(className="fas fa-chart-line dropdown-icon")
                                    ], className="dropdown-container")
                                ], width=12),
                            ], className="mb-4"),

                        ], className="settings-container")
                    ], width=12)
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
                    style={"position": "fixed", "top": 10, "left": 10, "zIndex": 1000},  # Posizionamento
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
                    className="btn-floating",  # Use the CSS class defined in styles.css
                ),

                # Floating Button
                dbc.Button(
                    children="Donate",  # Text on the button
                    id="donate-button",
                    className="btn-donating",  # Use the CSS class defined in styles.css
                ),

                # Floating Button
                dbc.Button(
                    children="Account",  # Text on the button
                    id="account-button",
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
                                    # Container per titolo e contatore
                                    html.Div(
                                        style={'position': 'relative'},  # Per il posizionamento assoluto del contatore
                                        children=[
                                            # Titolo centrato
                                            html.Div(
                                                html.H4("By Dani & Dati", className="mb-3"),
                                                className="text-center"
                                            ),
                                            # Contatore posizionato assolutamente
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

                                    # Resto del contenuto
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
                                                    html.A("Contribuisci allo sviluppo", href="https://github.com/daniele96l/backtester-dani",
                                                           style={ 'textDecoration': 'none'})
                                                ],
                                                style={'color': 'gray', 'marginTop': '1rem'}
                                            ),
                                            html.A(
                                                "Termini e Condizioni",
                                                href="https://danieleligato-eng.notion.site/Termini-e-Condizioni-196922846a1680ab8686d1a817717ae2",
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


        ])






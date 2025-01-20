import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash.dash_table
import plotly.graph_objects as go
import PlotLineChart as plc
import EfficentFonteer as ef
import webbrowser
import config
import logging
import warnings
import numpy as np
import statsmodels.api as sm


warnings.filterwarnings("ignore", category=UserWarning)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Show only errors

# Costanti
FILE_PATH = config.FILE_PATH
ETF_BASE_PATH = config.ETF_BASE_PATH
BASE_PATH = config.BASE_PATH

APP_TITLE = "PortfolioPilot"
# Define colors for benchmark and portfolio
benchmark_color = 'rgba(250, 128, 114, 0.7)'
portfolio_color = 'rgba(135, 206, 250, 0.7)'


def load_asset_list(file_path):
    """Carica e processa la lista degli asset da un file CSV."""
    try:
        data = pd.read_csv(file_path)
        asset_list = data['Fund'].apply(lambda x: x.split('.csv')[0]).tolist()
        return asset_list
    except FileNotFoundError:
        print(f"Errore: Il file {file_path} non è stato trovato.")
        return []
    except Exception as e:
        print(f"Si è verificato un errore durante il caricamento della lista degli asset: {e}")
        return []


def initialize_table():
    """Crea un DataFrame iniziale vuoto per la tabella del portafoglio."""
    return pd.DataFrame(columns=['ETF', 'Percentuale'])


def create_layout(asset_list, initial_table_data):
    year_range = list(range(1990, 2025))
    """Definisce il layout dell'app Dash utilizzando componenti Bootstrap."""
    return html.Div([
        # Header Container - Occupa tutta la larghezza dello schermo
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    html.Img(
                        src="/assets/Logo.png",  # Path to the logo in the assets folder
                        style={
                            'maxHeight': '100px',  # Set max height for the logo
                            'margin': 'auto',     # Center the logo
                            'display': 'block'
                        }
                    ),
                    width=12
                ),
                className='mb-4',  # Aggiunge un margine inferiore di 1.5rem
                style={
                    'backgroundColor': '#F8F9FA',  # Grigio chiaro
                    'padding': '20px 20px',          # Padding verticale
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'  # Ombra leggera per profondità
                }
            ),
        ], fluid=True),  # Container fluido per estendere l'header su tutta la larghezza

        # Main Content Container - Con margini orizzontali
        dbc.Container([
            # Riga di Selezione: Dropdown ETF e Slider Percentuale
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona un ETF (Scrivi il nome completo):", style={'color': '#000000'}),
                    dcc.Dropdown(
                        id='etf-dropdown',
                        options=[{'label': etf, 'value': etf} for etf in asset_list],#Posso cercare anche con il ticker? AKA una diversa asset list
                        placeholder="Seleziona un ETF",
                        className='mb-3',
                        style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                    )
                ], md=6),

                dbc.Col([
                    dbc.Label("Percentuale di Allocazione:", style={'color': '#000000'}),
                    dcc.Slider(
                        id='percentage-slider',
                        min=1,
                        max=100,
                        step=1,
                        value=100,
                        marks={i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "top", "always_visible": True},
                        updatemode='drag',
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
                        data=initial_table_data.to_dict('records'),
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
                               className='w-100 mt-4', style={'backgroundColor': '#8B4513', 'borderColor': '#8B4513'}),
                    md=2,  # Specifica la larghezza della colonna
                ),
                # Colonna per il dropdown
                dbc.Col([
                    dbc.Label("Scegli il tuo Benchmark (Opzionale):", style={'color': '#000000'}),
                    dcc.Dropdown(
                        id='benchmark-dropdown',
                        options=[{'label': etf, 'value': etf} for etf in asset_list],
                        placeholder="Seleziona un Benchmark",
                        className='mb-3',
                        style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                    )
                ], md=6),  # Specifica la larghezza della colonna
                # Colonna per la selezione degli anni
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
            dbc.Toast(
                id="allocation-error-toast",
                header="Stai superando il 100% di allocazione del tuo portafoglio, rimuovi o modifica le percentuali.",
                dismissable=True,
                duration=3000,  # Durata in millisecondi (2 secondi)
                is_open=False,  # Nascondi inizialmente
                style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000},  # Posizionamento
            ),

            dbc.Toast(
                [
                    html.Div([
                        html.P("🤖", style={"fontSize": "60px", "marginBottom": "10px"}),  # Emoji robot grande
                        html.P("Calcolo con algoritmi universitari...", style={"margin": "0", "fontSize": "22px", "fontWeight": "bold"})
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
                children="Info",  # Text on the button
                id="floating-button",
                style={
                    "backgroundColor": portfolio_color,  # Use the color variable
                    "color": "#000",  # Text color (adjust for contrast)

                },
                className="btn-floating",  # Use the CSS class defined in styles.css
            ),

            dbc.Button(
                "Esporta il Report in PDF.",
                id="save-pdf-button",
                style={
                    "backgroundColor": portfolio_color,  # Use the color variable
                    "color": "#000",  # Text color
                    "width": "100%",
                    "marginBottom": "50px",  # Add space below the button
                },
                className="mt-3",
            ),
            html.Div(id="hidden-div", style={"display": "none"}),

            dcc.Location(id="url", refresh=True)

        ], className='px-4', style={'backgroundColor': '#FFFFFF'})

    ])


def register_callbacks(app):
    """Registra tutti i callback per l'app Dash."""

    @app.callback(
        Output("portfolio-toast", "is_open"),
        Input("create-portfolio-button", "n_clicks"),
        State("portfolio-table", "data"),
        prevent_initial_call=True
    )
    def show_calculation_message(n_clicks, table_data):
        if n_clicks is None or not table_data:
            return False  # Non aprire il toast se non ci sono dati

        # Calcola l'allocazione totale
        try:
            total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
        except (ValueError, TypeError):
            return False  # Non aprire il toast se c'è un errore nei dati

        # Apri il toast solo se l'allocazione è corretta (100%)
        if total_percentage == 100:
            return True  # Mostra il toast se l'allocazione è esattamente 100%

        return False  # Non mostrare il toast se l'allocazione non è 100%

    @app.callback(
        Output("url", "href"),
        Input("floating-button", "n_clicks"),
        prevent_initial_call=True
    )
    def redirect_to_link(n_clicks):
        return "https://danieleligato-eng.notion.site/Versione-in-italiano-153922846a1680d7befcd164f03fd577"

    app.clientside_callback(
        """
          function(n_clicks) {
            if (n_clicks > 0) {
                // Open the print dialog; users can choose 'Save as PDF' in the dialog
                window.print();
            }
            return '';
        }
        """,
        Output('hidden-div', 'children'),  # Dummy output
        Input('save-pdf-button', 'n_clicks')  # Triggered by button clicks
    )

    # Callback per aggiungere un ETF alla tabella con la percentuale selezionata
    @app.callback(
        [Output('portfolio-table', 'data'),
         Output('allocation-error-toast', 'is_open')],
        [Input('add-etf-button', 'n_clicks')],
        [State('etf-dropdown', 'value'),
         State('percentage-slider', 'value'),
         State('portfolio-table', 'data')]
    )
    def add_etf_to_table(n_clicks, selected_etf, selected_percentage, current_data):
        if n_clicks is None:
            # Nessun clic ancora, restituisce i dati correnti invariati
            return current_data, False

        if n_clicks > 0:
            if not selected_etf:
                return current_data, False  # Nessun ETF selezionato, nessun cambiamento

            # Assicurati che current_data sia una lista di dizionari (righe della tabella)
            if current_data is None:
                current_data = []

            # Converti in DataFrame per una manipolazione più semplice
            current_df = pd.DataFrame(current_data)

            # Controlla se l'ETF esiste già nella tabella
            if 'ETF' in current_df.columns and not current_df[current_df['ETF'] == selected_etf].empty:
                return current_data, False  # Non aggiungere ETF duplicati

            # Assicurati che selected_percentage non sia None
            if selected_percentage is None:
                selected_percentage = 0

            # Controlla se l'aggiunta della nuova percentuale supera il 100%
            total_allocated = current_df['Percentuale'].sum() if not current_df.empty else 0
            if total_allocated + selected_percentage > 100:

                return current_data, True  # Mostra il toast di errore

            # Aggiungi il nuovo ETF alla tabella
            new_row = {
                "ETF": selected_etf,
                "Percentuale": selected_percentage,
            }
            current_data.append(new_row)  # Aggiungi la nuova riga ai dati della tabella

        return current_data, False


    # Callback per gestire la creazione del portafoglio
    @app.callback(
        [Output('portfolio-feedback', 'children'),
         Output('portfolio-data', 'data'),
         Output('assets-data', 'data'),
         Output('start-year-dropdown', 'options'),  # Dynamically update start year options
         Output('end-year-dropdown', 'options')],  # Dynamically update end year options
        [Input('create-portfolio-button', 'n_clicks')],
        [State('portfolio-table', 'data'),
         State('benchmark-dropdown', 'value'),
         State('start-year-dropdown', 'value'),
         State('end-year-dropdown', 'value')]
    )
    def create_portfolio(n_clicks, table_data, benchmark, start_year, end_year):

        # Set default years if not provided
        start_year = start_year or 1990
        end_year = end_year or 2024
        start_date = pd.Timestamp(f'{start_year}-01-01')
        end_date = pd.Timestamp(f'{end_year}-12-31')

        # Validate the date range
        if start_date > end_date:
            return "L'anno di inizio deve essere precedente all'anno di fine.", dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Convert input dates to datetime objects if they exist
        start_dt = pd.to_datetime(start_date) if start_date else None
        end_dt = pd.to_datetime(end_date) if end_date else None

        if n_clicks is None:
            return "", dash.no_update,  dash.no_update, dash.no_update, dash.no_update

        if n_clicks > 0:
            if not table_data:
                return "Nessun ETF nel portafoglio da creare.", dash.no_update, dash.no_update, dash.no_update, dash.no_update
            # Calcola l'allocazione totale
            try:
                total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
            except (ValueError, TypeError):
                return "Valore percentuale non valido rilevato.", dash.no_update, dash.no_update, dash.no_update, dash.no_update

            if total_percentage != 100:
                return f"L'allocazione totale deve essere esattamente del 100%. Totale attuale: {total_percentage:.2f}%.", dash.no_update, dash.no_update, dash.no_update, dash.no_update

            # Converti i dati della tabella in DataFrame
            df = pd.DataFrame(table_data)
            nomi_etf = df['ETF']
            indici = match_asset_name(nomi_etf)

            dati = importa_dati(indici)
            #dati = dati.loc[:, ~dati.columns.duplicated()] #Rimosso perchè dava problemi se mettevo due ETF uguali tra la lista

            #Calcola i ritorni pe ogni asset

            pct_change = dati.pct_change()
            #Drop nan values
            pct_change = pct_change.dropna()
            #Scala i ritorni per il peso e poi fanne la media
            dati_scalati = pct_change * df['Percentuale'].values/100 #WHAT IF I CLICK ON THE SAME INDEX?

            dati_scalati['Portfolio_return'] = dati_scalati.sum(axis=1)

            dati_scalati['Portfolio'] = 100 * (1 + dati_scalati['Portfolio_return']).cumprod()


            dati_scalati = dati_scalati.drop(columns=['Portfolio_return'])

            dati_scalati = dati_scalati.drop(dati.columns, axis=1)
            portfolio_con_benchmark = dati_scalati.copy()

            if benchmark:
                indice_benchmark = match_asset_name([benchmark])
                dati_benckmark = importa_dati(indice_benchmark)
                dati_benckmark = dati_benckmark.loc[:, ~dati_benckmark.columns.duplicated()]
                portfolio_con_benchmark = dati_scalati.join(dati_benckmark[indice_benchmark[0]], how='inner', rsuffix='_benchmark')
                portfolio_con_benchmark['Benchmark'] = portfolio_con_benchmark[indice_benchmark[0]] / portfolio_con_benchmark[indice_benchmark[0]].iloc[0] * 100
                portfolio_con_benchmark = portfolio_con_benchmark.drop(columns=[indice_benchmark[0]])
                portfolio_con_benchmark['Portfolio'] = portfolio_con_benchmark['Portfolio'] / portfolio_con_benchmark['Portfolio'].iloc[0] * 100

            # Get the first and last dates of the portfolio
            first_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[0])
            last_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[-1])

            if (first_portfolio_date > end_dt):
                end_dt = last_portfolio_date
                start_dt = first_portfolio_date

            # Apply slicing and normalization based on conditions
            if (start_dt and start_dt > first_portfolio_date ):
                dati = dati.loc[start_dt:]
                dati = (dati / dati.iloc[0]) * 100
                portfolio_con_benchmark = portfolio_con_benchmark.loc[start_dt:]
                portfolio_con_benchmark = (portfolio_con_benchmark / portfolio_con_benchmark.iloc[0]) * 100

            if (end_dt and end_dt < last_portfolio_date):
                portfolio_con_benchmark = portfolio_con_benchmark.loc[:end_dt]
                dati = dati.loc[:end_dt]


            first_year = first_portfolio_date.year
            dynamic_years_start = [{'label': str(year), 'value': year} for year in range(first_year, 2025)] #Fist year is the fist year of the portfolio
            dynamic_years_end = [{'label': str(year), 'value': year} for year in range(first_year, 2025)] #Start year è il primo anno dopo l'anno minimo settato dall'utente

            # Fornisci feedback all'utente e salva i dati nel Store
            portfolio_con_benchmark.reset_index(inplace=True)

            return "", portfolio_con_benchmark.to_dict('records'), dati.to_dict('records'), dynamic_years_start, dynamic_years_end

        return "", "","", dash.no_update, dash.no_update

    # Callback per elaborare i dati del portafoglio e fornire feedback aggiuntivo
    def match_asset_name(nomi_assets):
        mapping = pd.read_csv(FILE_PATH)
        nomi_indici = [mapping[mapping['Fund'] == asset]['Index'].values[0] for asset in nomi_assets if
                       asset in mapping['Fund'].values]
        return nomi_indici

    def importa_dati(nomi_indici):
        dati = None  # Initialize an empty dataframe for merging
        for i in nomi_indici:
            # Read the data and set Date as the index
            temp_data = pd.read_csv(
                f"{ETF_BASE_PATH}/{i}.csv",  # Use the base path
                parse_dates=['Date'],
            ).set_index('Date')

            if dati is None:
                dati = temp_data  # For the first dataframe, initialize `dati`
            else:
                dati = pd.concat([dati, temp_data], axis=1)  # Concatenate on index (Date)

        dati.dropna(inplace=True)  # Drop rows with missing values
        #Normalize all the columns making them start from 100
        dati = dati / dati.iloc[0] * 100

        return dati

    def calculate_rolling_returns(portfolio_df, period):
        rolling_returns = portfolio_df.copy()
        rolling_returns = rolling_returns.set_index('Date')
        rolling_returns = rolling_returns.pct_change().rolling(window=period).sum()
        rolling_returns = rolling_returns.dropna()
        rolling_returns = rolling_returns.reset_index()
        return rolling_returns
    def add_rolling_traces(portfolio_df, period, portfolio_color,column_except_date):
        if(len(portfolio_df) < period):
            rolling = go.Figure()
            return rolling.add_trace(go.Scatter(x=[0], y=[0], mode='text', text=f'Non ci sono abbastanza dati per calcolare i rendimenti rolling per {period} mesi'))
        else:
            rolling_returns = calculate_rolling_returns(portfolio_df, period)
            return plc.plot_line_chart_rolling(column_except_date, rolling_returns, portfolio_color, benchmark_color,period)

    def import_fama_french():
        fama_french = pd.read_csv(f"{BASE_PATH}/Developed_5_Factors.csv", parse_dates=['Date'])
        fama_french = fama_french.set_index('Date')
        fama_french = fama_french / 100
        return fama_french

    # Function to calculate factor exposure directly inside the function
    def calculate_factor_exposure(portfolio_df):
        # Calculate the percentage change (returns) and drop missing values
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
        portfolio_df.set_index('Date', inplace=True)

        # Calculate returns for the portfolio and rename the column to 'Adj Close'
        data = portfolio_df.pct_change().dropna()
        data["Adj Close"] = data # Rename the column to 'Adj Close'

        fundsret = data["Adj Close"]

        # Import the Fama-French factors
        factors = import_fama_french()

        # Merge portfolio returns and factors using an inner join on the index (Date)
        merge = pd.merge(fundsret, factors, left_index=True, right_index=True, how='inner')

        # Adjust the portfolio returns by subtracting the risk-free rate (RF)
        merge["Adj Close"] = merge["Adj Close"] - merge["RF"]

        # Normalize the factors by dividing by 100
        merge[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]] = merge[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]] / 100

        # Set the dependent variable (y) as the portfolio excess returns
        y = merge["Adj Close"]

        # Set the independent variables (X) as the factors (Mkt-RF, SMB, HML, RMW, CMA)
        X = merge[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]]
        X_sm = sm.add_constant(X)  # Add a constant to the model for the intercept

        # Fit the OLS regression model
        model = sm.OLS(y, X_sm)
        results = model.fit()

        # Extract the results summary
        results_summary = results.summary()
        tables = results_summary.tables

        # Extract coefficients and variable names from the regression results
        dataframes = []
        for i, table in enumerate(tables):
            df = pd.DataFrame(table[1:], columns=table[0])
            dataframes.append(df)

        coef_data = dataframes[1].iloc[:, 1]
        coef_data = coef_data.apply(lambda x: float(x.data.strip()))
        variable_names = dataframes[1].iloc[:, 0]

        # Exclude first and last values for better visualization
        coef_data_to_plot = coef_data[1:-1]
        variable_names_to_plot = variable_names[1:-1]

        # Return the coefficients (exposures) and the factor names
        return coef_data_to_plot, variable_names_to_plot

    @app.callback(
        Output('additional-feedback', 'children'),  # Output to display the charts
        [Input('portfolio-data', 'data'),
         Input('assets-data', 'data')]
    )
    def plot_data(portfolio_data, dati):  # ----------- KING #TODO Esportare tutti i grafici con un bottone
        # Convert data back to DataFrame

        portfolio_df = pd.DataFrame(portfolio_data)
        dati_df = pd.DataFrame(dati) #Sto ricevendo un DICT e non un DataFrame, quindi le colonne duplicate erano state rimosse
        # Questo vuol dire che se metto due ETF uguali nella lista, uno dei due verrà rimosso

        # Ensure 'Date' column is datetime for calculations
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])

        rolling_periods = [36, 60, 120]

        column_except_date = [col for col in portfolio_df.columns if col != 'Date']

        rolling1 = go.Figure()
        rolling2 = go.Figure()
        rolling3 = go.Figure()

        rolling1 = add_rolling_traces(portfolio_df, rolling_periods[0], portfolio_color,column_except_date)
        rolling2 = add_rolling_traces(portfolio_df, rolling_periods[1], portfolio_color,column_except_date)
        rolling3 = add_rolling_traces(portfolio_df, rolling_periods[2], portfolio_color,column_except_date)

        drawdown = go.Figure()
        drawdown = plc.plot_drawdown(portfolio_df, portfolio_color,benchmark_color,column_except_date)

        # Calculate factor exposure for the portfolio
        factor_exposure_portfolio, factor_names = calculate_factor_exposure(portfolio_df[["Portfolio","Date"]])
        #If the benchmark column exists calculate the factor exposure for the benchmark
        if 'Benchmark' in portfolio_df.columns:
            factor_exposure_benchmark, factor_names = calculate_factor_exposure(portfolio_df[["Benchmark","Date"]])



        # Calculate CAGR and Volatility for each column except 'Date'
        cagr = {}
        volatility = {}
        sharpe_ratio = {}


        for column in column_except_date:
            start_value = portfolio_df[column].iloc[0]
            end_value = portfolio_df[column].iloc[-1]
            num_years = (portfolio_df['Date'].iloc[-1] - portfolio_df['Date'].iloc[0]).days / 365.25
            cagr[column] = ((end_value / start_value) ** (1 / num_years) - 1) * 100  # CAGR as percentage
            volatility[column] = portfolio_df[column].pct_change().std() * (12 ** 0.5) * 100
            sharpe_ratio[column] = cagr[column] / volatility[column] if volatility[column] != 0 else 0

        # Round the values
        cagr = {k: round(v, 2) for k, v in cagr.items()}
        volatility = {k: round(v, 2) for k, v in volatility.items()}
        sharpe_ratio = {k: round(v, 2) for k, v in sharpe_ratio.items()}

        # Create a DataFrame for the metrics
        metrics_df = pd.DataFrame([cagr, volatility,sharpe_ratio], index=['CAGR', 'Volatility','Sharpe Ratio']).reset_index()
        metrics_df = metrics_df.rename(columns={'index': 'Metric'})

        # Melt the DataFrame for plotting
        metrics_melted = pd.melt(metrics_df, id_vars='Metric', var_name='Portfolio', value_name='Value')

        # Split the metrics into separate DataFrames for each metric
        cagr_data = metrics_melted[metrics_melted["Metric"] == "CAGR"]
        volatility_data = metrics_melted[metrics_melted["Metric"] == "Volatility"]
        sharpe_data = metrics_melted[metrics_melted["Metric"] == "Sharpe Ratio"]

        correlation_matrix = dati_df.corr()

        scatter_fig,pie_fig = ef.calcola_frontiera_efficente(dati_df) # TODO non plottare gli indici ma i nomi degli etf

        custom_colorscale = [
            [0, benchmark_color],  # Start of the scale
            [1, portfolio_color]  # End of the scale
        ]

        # Assuming 'factor_names' is a list of factor names (probably from the regression results)
        factor_names = [cell.data for cell in factor_names]

        # Map the factor names to Italian using the dictionary
        factor_name_translation = {
            "Mkt-RF": "Mercato-RF",
            "SMB": "Small Cap",
            "HML": "Value",
            "RMW": "Profitabilità",
            "CMA": "Investimenti conservativi",
            "RF": "Tasso privo di rischio",
        }

        # Apply the translation to the factor names
        factor_names_italian = [factor_name_translation.get(name, name) for name in factor_names]

        # Create a bar chart for the factor exposure
        factor_exposure_fig = go.Figure()
        factor_exposure_fig.add_trace(go.Bar(
            x=factor_names_italian,  # Use translated names here
            y=factor_exposure_portfolio,
            name="Portfolio",
            marker=dict(color=portfolio_color)
        ))

        if 'Benchmark' in portfolio_df.columns:
            factor_exposure_fig.add_trace(go.Bar(
                x=factor_names_italian,  # Use translated names here
                y=factor_exposure_benchmark,
                name="Benchmark",
                marker=dict(color=benchmark_color)
            ))

        factor_exposure_fig.update_layout(
            title="Esposizione ai Fattori",
            xaxis_title="Fattori",
            yaxis_title="Esposizione",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        correlation_fig = go.Figure()
        correlation_fig.add_trace(go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale=custom_colorscale
        ))

        correlation_fig.update_layout(
            title="Correlazione tra gli Asset",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )


        sharpe_fig = go.Figure()
        sharpe_fig.add_trace(go.Bar(
            x=sharpe_data["Portfolio"],
            y=sharpe_data["Value"],
            name="Sharpe Ratio",
            marker=dict(color=[portfolio_color, benchmark_color])
        ))

        sharpe_fig.update_layout(
            title="Sharpe Ratio per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Sharpe Ratio",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        # Create separate bar charts for CAGR and Volatility
        cagr_fig = go.Figure()
        cagr_fig.add_trace(go.Bar(
            x=cagr_data["Portfolio"],
            y=cagr_data["Value"],
            name="Ritorno Composto Annuo",
            marker=dict(color=[portfolio_color, benchmark_color])


        ))
        cagr_fig.update_layout(
            title="Ritorno per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Ritorno (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        volatility_fig = go.Figure()
        volatility_fig.add_trace(go.Bar(
            x=volatility_data["Portfolio"],
            y=volatility_data["Value"],
            name="Volatility",
            marker=dict(color=[portfolio_color, benchmark_color])
        ))
        volatility_fig.update_layout(
            title="Volatilità per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Volatilità (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        portfolio_fig = plc.plot_line_chart(column_except_date, portfolio_df, portfolio_color, benchmark_color)

        # Return both graphs side by side, and the line chart below
        return html.Div([
            html.Div(dcc.Graph(figure=portfolio_fig), style={'width': '100%'}),
            html.Div(dcc.Graph(figure=cagr_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=volatility_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=sharpe_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=rolling1), style={'width': '100%'}), #Rolling 3y
            html.Div(dcc.Graph(figure=rolling2), style={'width': '100%'}), #Rolling 5y
            html.Div(dcc.Graph(figure=rolling3), style={'width': '100%'}), #Rolling 10y
            html.Div(dcc.Graph(figure=drawdown), style={'width': '100%'}),  # Drawdown
            html.Div(dcc.Graph(figure=correlation_fig), style={'width': '100%'}),  # Correlation between assets
            html.Div(dcc.Graph(figure=scatter_fig), style={'width': '100%'}),  # Efficent fronteer
            html.Div(dcc.Graph(figure=pie_fig), style={'width': '100%'}),  # Efficent fronteer
            html.Div(dcc.Graph(figure=factor_exposure_fig), style={'width': '100%'}),  # Factor Exposure
        ])


def main():
    # Carica la lista degli asset
    asset_list = load_asset_list(FILE_PATH)

    # Inizializza l'app Dash con il tema Bootstrap e stili personalizzati
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = APP_TITLE

    # Inizializza i dati della tabella
    initial_table_data = initialize_table()

    # Imposta il layout dell'app
    app.layout = create_layout(asset_list, initial_table_data)

    # Registra i callback
    register_callbacks(app)

    # Esegui l'app
    app.run_server(port=80, host='0.0.0.0')


if __name__ == '__main__':
    main()

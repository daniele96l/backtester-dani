import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash.dash_table
import plotly.graph_objects as go
from Frontend import plot_line_chart as plc
import efficent_fronteer as ef
import logging
import warnings
from Frontend.layout import LayoutManager
from factor_regression import calculate_factor_exposure
from imports_handler import match_asset_name, importa_dati,load_asset_list
from portfolio_allocation import PortfolioAllocation
from math_logic import MathLogic

from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, INDEX_LIST_FILE_PATH

warnings.filterwarnings("ignore", category=UserWarning)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Show only errors

# Define style constant
LOGIN_INDICATOR_STYLE = {
    "position": "fixed",
    "top": "15px",  # Ridotto da 20px
    "right": "15px",  # Ridotto da 20px
    "fontSize": "14px",  # Ridotto da 16px
    "zIndex": 1500,
    "cursor": "default",
    "transition": "opacity 0.3s ease",
    "display": "flex",
    "alignItems": "center",
    "gap": "6px",  # Ridotto da 8px
    "backgroundColor": "rgba(255, 255, 255, 0.9)",
    "padding": "6px 10px",  # Ridotto da 8px 12px
    "borderRadius": "15px",  # Ridotto da 20px
    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
}


def register_callbacks(app):
    """Registra tutti i callback per l'app Dash."""

    @app.callback(
        Output("portfolio-toast", "is_open"),
        Input("create-portfolio-button", "n_clicks"),
        State("portfolio-table", "data"),
        State('start-year-dropdown', 'value'),
        State('end-year-dropdown', 'value'),
        prevent_initial_call=True
    )
    def show_calculation_message(n_clicks, table_data, start_year, end_year):
        if n_clicks is None or not table_data:
            return False  # Non aprire il toast se non ci sono dati

        start_year = start_year or 1970
        end_year = end_year or 2024
        start_date = pd.Timestamp(f'{start_year}-01-01')
        end_date = pd.Timestamp(f'{end_year}-12-31')

        # Validate the date range
        if start_date > end_date:
            return False

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
        [
            Output("url", "href", allow_duplicate=True),
        ],
        [
            Input("tutorial-button", "n_clicks"),
            Input("donate-button", "n_clicks"),
        ],
        prevent_initial_call=True
    )
    def handle_tutorial_and_donate(n_tutorial, n_donate):
        """Handles button clicks for tutorial and donation actions."""

        ctx = dash.callback_context

        # If no button was clicked, do nothing
        if not ctx.triggered:
            return [dash.no_update]

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        tutorial_link = "https://danieleligato-eng.notion.site/Versione-in-italiano-153922846a1680d7befcd164f03fd577"
        donate_link = "https://www.paypal.com/donate/?hosted_button_id=M378MEXMSSQT6"

        if triggered_id == "tutorial-button":
            return [tutorial_link]
        elif triggered_id == "donate-button":
            return [donate_link]

        return [dash.no_update]

    # Callback per gestire il modale di login
    @app.callback(
        [
            Output("login-modal", "is_open"),
            Output("Work-in-progress-toast", "is_open"),
        ],
        [
            Input("account-button", "n_clicks"),
            Input("login-trigger", "n_clicks"),
            Input("close-modal", "n_clicks"),
        ],
        [State("login-state", "data")],
        prevent_initial_call=True
    )
    def handle_account_and_close(n_account, n_emoji, n_close, login_state):
        """Handles button clicks for account and modal close actions."""
        ctx = dash.callback_context

        # Se nessun click è stato fatto, mantieni tutto chiuso
        if not ctx.triggered or all(x is None for x in [n_account, n_emoji, n_close]):
            return False, False

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id in ["account-button", "login-trigger"]:
            return True, dash.no_update
        elif triggered_id == "close-modal":
            return False, dash.no_update

        return False, False

    @app.callback(
        [
            Output("login-indicator", "children"),
            Output("login-indicator", "style")
        ],
        [
            Input("login-state", "data"),
            Input("url", "pathname")
        ],
    )
    def update_login_indicator(login_state, pathname):
        """Updates the login indicator with emoji and text based on login state."""
        if login_state and login_state.get("logged_in"):
            emoji = "👤"
            text = f"Bentornato: {login_state.get('username')}"
            style = {
                **LOGIN_INDICATOR_STYLE,
                "color": "#198754",  # Green color for logged in state
                "cursor": "pointer"  # Aggiunto per indicare cliccabilità
            }
        else:
            emoji = "👻"
            text = "Accesso non effettuato"
            style = {
                **LOGIN_INDICATOR_STYLE,
                "color": "#6c757d",  # Gray color for logged out state
                "cursor": "pointer"  # Aggiunto per indicare cliccabilità
            }

        return [
            html.Div([
                html.Span(emoji, style={"fontSize": "16px"}),
                html.Span(text, className="login-text")
            ],
                id="login-trigger",  # Aggiunto ID per il trigger
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "cursor": "pointer"  # Aggiunto per indicare cliccabilità
                }),
            style
        ]

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
         State('percentage-input', 'value'),
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

            if selected_percentage > 100:
                selected_percentage = 100
            if selected_percentage <= 0:
                selected_percentage = 0.1

            selected_percentage = round(selected_percentage, 2)

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

    @app.callback(
        Output('remaining-percentage', 'children'),
        [Input('portfolio-table', 'data')]
    )
    def update_remaining_percentage(table_data):
        if not table_data:
            return html.Div([
                html.Span("Totale corrente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
                html.Span("0.00%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'marginRight': '15px'}),
                html.Span("Percentuale rimanente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
                html.Span("100.00%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'color': '#dc3545'})
            ])

        # Calcola la somma delle percentuali
        total = sum(float(row.get('Percentuale', 0)) for row in table_data)
        remaining = 100 - total

        # Determina il colore della percentuale rimanente
        color = '#198754' if remaining == 0 else '#dc3545'  # Verde se 0, rosso altrimenti

        return html.Div([
            html.Span("Totale corrente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
            html.Span(f"{total:.2f}%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'marginRight': '15px'}),
            html.Span("Percentuale rimanente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
            html.Span(f"{remaining:.2f}%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'color': color})
        ])


    # Callback per gestire la creazione del portafoglio
    @app.callback(
        [Output('portfolio-feedback', 'children'),
         Output('portfolio-data', 'data'),
         Output('assets-data', 'data'),
         Output('start-year-dropdown', 'options'),  # Dynamically update start year options
         Output('end-year-dropdown', 'options'),  # Dynamically update end year options
         Output('pesi-correnti', 'data')],  # New output for pesi_correnti
        [Input('create-portfolio-button', 'n_clicks')],
        [State('portfolio-table', 'data'),
         State('benchmark-dropdown', 'value'),
         State('start-year-dropdown', 'value'),
         State('end-year-dropdown', 'value')]
    )
    def create_portfolio(n_clicks, table_data, benchmark, start_year, end_year):
        # Set default years if not provided
        warnings_data_benchmark = []
        start_year = start_year or 1970
        end_year = end_year or 2024
        start_date = pd.Timestamp(f'{start_year}-01-01')
        end_date = pd.Timestamp(f'{end_year}-12-31')

        # Validate the date range
        if start_date > end_date:
            return "L'anno di inizio deve essere precedente all'anno di fine.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Convert input dates to datetime objects if they exist
        start_dt = pd.to_datetime(start_date) if start_date else None
        end_dt = pd.to_datetime(end_date) if end_date else None

        if n_clicks is None:
            return "", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if n_clicks > 0:
            if not table_data:
                return "Nessun ETF nel portafoglio da creare.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            # Calcola l'allocazione totale
            try:
                total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
            except (ValueError, TypeError):
                return "Valore percentuale non valido rilevato.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

            if total_percentage != 100:
                return f"L'allocazione totale deve essere esattamente del 100%. Totale attuale: {total_percentage:.2f}%.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

            # Converti i dati della tabella in DataFrame
            df = pd.DataFrame(table_data)
            nomi_etf = df['ETF']
            indici = match_asset_name(nomi_etf)

            dati, warnings_data = importa_dati(indici)

            #Calcola i ritorni per ogni asset
            pct_change = dati.pct_change()
            pct_change = pct_change.dropna()
            # Scala i ritorni per il peso e poi fanne la media
            dati_scalati = pct_change * df['Percentuale'].values / 100 #Moltiplica i ritorni di ogni per il loro peso nel portafoglio in modo da trovare il ritorno del portafoglio

            pesi_correnti = df['Percentuale'].values / 100

            dati_scalati['Portfolio_return'] = dati_scalati.sum(axis=1)
            dati_scalati['Portfolio'] = 100 * (1 + dati_scalati['Portfolio_return']).cumprod()

            dati_scalati = dati_scalati.drop(columns=['Portfolio_return'])

            dati_scalati = dati_scalati.drop(dati.columns, axis=1)
            portfolio_con_benchmark = dati_scalati.copy()

            if benchmark:
                indice_benchmark = match_asset_name([benchmark])
                dati_benckmark, warnings_data_benchmark = importa_dati(indice_benchmark)
                dati_benckmark = dati_benckmark.loc[:, ~dati_benckmark.columns.duplicated()]
                portfolio_con_benchmark = dati_scalati.join(dati_benckmark[indice_benchmark[0]], how='inner',
                                                            rsuffix='_benchmark')
                portfolio_con_benchmark['Benchmark'] = portfolio_con_benchmark[indice_benchmark[0]] / \
                                                       portfolio_con_benchmark[indice_benchmark[0]].iloc[0] * 100
                portfolio_con_benchmark = portfolio_con_benchmark.drop(columns=[indice_benchmark[0]])
                portfolio_con_benchmark['Portfolio'] = portfolio_con_benchmark['Portfolio'] / \
                                                       portfolio_con_benchmark['Portfolio'].iloc[0] * 100
                if warnings_data[0] < warnings_data_benchmark[0]:
                    warnings_data = warnings_data_benchmark

            warnings_data_string = f"La data più lontana disponibile per l'analisi è {warnings_data[0]} poiché l'ETF {warnings_data[1]} ha dati disponibili solo a partire da quel momento."

            # Get the first and last dates of the portfolio
            first_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[0])
            last_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[-1])

            if (first_portfolio_date > end_dt):
                end_dt = last_portfolio_date
                start_dt = first_portfolio_date

            # Apply slicing and normalization based on conditions
            if (start_dt and start_dt > first_portfolio_date):
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

            # Convert pesi_correnti to a format suitable for dcc.Store
            pesi_correnti_dict = {'weights': pesi_correnti.tolist()}

            return warnings_data_string, portfolio_con_benchmark.to_dict('records'), dati.to_dict(
                'records'), dynamic_years_start, dynamic_years_end, pesi_correnti_dict

        return "", "", "", dash.no_update, dash.no_update, dash.no_update



    @app.callback(
        [Output("menu-button", "className"),
         Output("interval-component", "disabled")],
        [Input("menu-button", "n_clicks"),
         Input("interval-component", "n_intervals")],
        [State("menu-button", "className")]
    )
    def toggle_buttons(n_clicks, n_intervals, current_class):
        if n_clicks:
            if "active" in current_class:
                return "btn-menu", True
            else:
                return "btn-menu active", False
        elif n_intervals > 0:
            return "btn-menu", True
        return "btn-menu", True

    @app.callback(
        Output('additional-feedback', 'children'),  # Output to display the charts
        [Input('portfolio-data', 'data'),
         Input('assets-data', 'data'),
         Input('pesi-correnti', 'data')]
    )
    def plot_data(portfolio_data, dati, pesi_correnti):  # ----------- KING

        portfolio_df = pd.DataFrame(portfolio_data)
        dati_df = pd.DataFrame(dati) #Sto ricevendo un DICT e non un DataFrame, quindi le colonne duplicate erano state rimosse
        # Questo vuol dire che se metto due ETF uguali nella lista, uno dei due verrà rimosso

        indici_usati = dati_df.columns
        country_allocation = PortfolioAllocation().calculate_country_allocation(indici_usati, pesi_correnti)
        sector_allocation = PortfolioAllocation().calculate_sector_allocation(indici_usati, pesi_correnti)

        # Ensure 'Date' column is datetime for calculations
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
        rolling_periods = [36, 60, 120]
        column_except_date = [col for col in portfolio_df.columns if col != 'Date']

        rolling1, rolling2, rolling3 = MathLogic.calculate_3_rolling_returns(portfolio_df, rolling_periods,column_except_date)

        drawdown = plc.plot_drawdown(portfolio_df, PORTFOLIO_COLOR,BENCHMARK_COLOR,column_except_date)

        # Calculate factor exposure for the portfolio
        factor_exposure_portfolio, factor_names = calculate_factor_exposure(portfolio_df[["Portfolio","Date"]])
        if 'Benchmark' in portfolio_df.columns:    #If the benchmark column exists calculate the factor exposure for the benchmark
            factor_exposure_benchmark, factor_names = calculate_factor_exposure(portfolio_df[["Benchmark","Date"]])

        scatter_fig,pie_fig,portfolio_returns = ef.calcola_frontiera_efficente(dati_df,pesi_correnti)

        cagr_data, volatility_data, sharpe_data = MathLogic.calculate_performance_metrics(portfolio_df, portfolio_returns,column_except_date)

        correlation_matrix = dati_df.corr()

        custom_colorscale = [
            [0, BENCHMARK_COLOR],  # Start of the scale
            [1, PORTFOLIO_COLOR]  # End of the scale
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
            marker=dict(color=PORTFOLIO_COLOR)
        ))

        if 'Benchmark' in portfolio_df.columns:
            factor_exposure_fig.add_trace(go.Bar(
                x=factor_names_italian,  # Use translated names here
                y=factor_exposure_benchmark,
                name="Benchmark",
                marker=dict(color=BENCHMARK_COLOR)
            ))

        factor_exposure_fig.update_layout(
            title="Esposizione ai Fattori globali di Fama-French",
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
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])
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
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])


        ))
        cagr_fig.update_layout(
            title="Ritorno Aritmetico Dei Portafogli",
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
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])
        ))
        volatility_fig.update_layout(
            title="Volatilità per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Volatilità (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        titolo_warning = html.Div(
            children="Funzione sperimentale, potrebbero esserci errori o dati mancanti",
            style={
                'textAlign': 'center',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': 'darkred',
                'marginBottom': '20px'
            }
        )

        # Define pastel colors
        pastel_colors = [
            '#AEC6CF', '#FFD1DC', '#FFB3DE', '#B5EAEA', '#C2F0C2',
            '#FFBCB3', '#FFCC99', '#D9EAD3', '#D5A6BD', '#FF6666'
        ]

        # Create a pie chart for the country allocation
        country_fig = go.Figure()
        country_fig.add_trace(go.Pie(
            labels=country_allocation['Paese'],
            values=country_allocation['Peso'],
            hole=0.3,
            textinfo='percent+label',  # Show both the percentage and label
            insidetextorientation='horizontal',  # Make text horizontal inside the pie
            textfont=dict(size=14, color='black'),  # Style text for better visibility
            marker=dict(
                colors=pastel_colors,  # Use pastel color palette
                line=dict(color='white', width=2)  # Add white border to make slices pop
            ),
            hoverinfo='label+percent',  # Display label and percentage on hover
            pull=[0.1, 0, 0, 0, 0, 0, 0, 0],  # Slightly "explode" the first slice for emphasis (optional)
        ))

        country_fig.update_layout(
            title="Allocazione geografica (Azioni & Obbligazioni)",
            title_x=0.5,  # Center the title
            plot_bgcolor='rgba(0,0,0,0)',  # Remove the background color for a cleaner look
            margin=dict(t=40, b=40, l=40, r=40),  # Adjust the margins for better spacing
        )

        # Create a pie chart for the sector allocation
        sector_fig = go.Figure()
        sector_fig.add_trace(go.Pie(
            labels=sector_allocation['Settore'],
            values=sector_allocation['Peso'],
            hole=0.3,
            textinfo='percent+label',  # Show both the percentage and label
            insidetextorientation='horizontal',  # Make text horizontal inside the pie
            textfont=dict(size=14, color='black'),  # Style text for better visibility
            marker=dict(
                colors=pastel_colors,  # Use pastel color palette
                line=dict(color='white', width=2)  # Add white border to make slices pop
            ),
            hoverinfo='label+percent',  # Display label and percentage on hover
            pull=[0, 0.1, 0, 0, 0, 0, 0, 0],  # Slightly "explode" the second slice for emphasis (optional)
        ))

        sector_fig.update_layout(
            title="Allocazione azionaria per settore",
            title_x=0.5,  # Center the title
            plot_bgcolor='rgba(0,0,0,0)',  # Remove the background color for a cleaner look
            margin=dict(t=40, b=40, l=40, r=40),  # Adjust the margins for better spacing
        )

        portfolio_fig = plc.plot_line_chart(column_except_date, portfolio_df, PORTFOLIO_COLOR, BENCHMARK_COLOR)
        multiple_assets_plot = html.Div([
            html.Div(dcc.Graph(figure=correlation_fig), style={'width': '100%'}),  # Correlation between assets
            html.Div(dcc.Graph(figure=scatter_fig), style={'width': '100%'}),  # Efficient frontier
            html.Div(dcc.Graph(figure=pie_fig), style={'width': '100%'}),  # Efficient frontier
        ])

        single_assets_plot = html.Div([
            html.Div(dcc.Graph(figure=portfolio_fig), style={'width': '100%'}),
            html.Div(dcc.Graph(figure=cagr_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=volatility_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=sharpe_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=rolling1), style={'width': '100%'}),  # Rolling 3y
            html.Div(dcc.Graph(figure=rolling2), style={'width': '100%'}),  # Rolling 5y
            html.Div(dcc.Graph(figure=rolling3), style={'width': '100%'}),  # Rolling 10y
            html.Div(dcc.Graph(figure=drawdown), style={'width': '100%'}),  # Drawdown
            html.Div(titolo_warning, style={'width': '100%'}),  # Fixed width format
            html.Div([
                html.Div(dcc.Graph(figure=country_fig), style={'width': '50%', 'display': 'inline-block'}),  # Country Allocation
                html.Div(dcc.Graph(figure=sector_fig), style={'width': '50%', 'display': 'inline-block'})  # Sector Allocation
            ], style={'width': '100%'}),
            html.Div(dcc.Graph(figure=factor_exposure_fig), style={'width': '100%'})  # Factor Exposure
        ])

        if len(pesi_correnti["weights"]) > 1:  # Return all the plots if there is more than one ETF
            total_plot = [single_assets_plot, multiple_assets_plot]
        else:
            total_plot = [single_assets_plot]  # Wrap in a list for consistency

        # Return both graphs side by side, and the line chart below
        return html.Div(total_plot)


def main():
    # Carica la lista degli asset
    asset_list = load_asset_list(INDEX_LIST_FILE_PATH)

    # Inizializza l'app Dash con il tema Bootstrap e stili personalizzati
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = APP_TITLE

    # Inizializza i dati della tabella
    initial_table_data = pd.DataFrame(columns=['ETF', 'Percentuale'])

    # Imposta il layout dell'app
    app.layout = LayoutManager.create_layout(asset_list, initial_table_data,app)

    # Registra i callback
    register_callbacks(app)

    # Esegui l'app
    app.run_server(port=SERVER_PORT, host=SERVER_HOST)


if __name__ == '__main__':
    main()

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash.dash_table
import plotly.graph_objects as go
import PlotLineChart as plc
import EfficentFonteer as ef
import logging
import warnings
import statsmodels.api as sm
from Layout import LayoutManager
from Factor_regression import calculate_factor_exposure
from ImportsHandler import match_asset_name, importa_dati,load_asset_list

from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, DEV_FIVE_FACTORS_FILE_PATH, INDEX_LIST_FILE_PATH, ETF_BASE_PATH

warnings.filterwarnings("ignore", category=UserWarning)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Show only errors

# Define style constant
LOGIN_INDICATOR_STYLE = {
    "position": "fixed",
    "top": "20px",
    "right": "20px",
    "fontSize": "24px",
    "zIndex": 1500,
    "cursor": "default",
    "transition": "opacity 0.3s ease"
}


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

        print(f"{triggered_id} clicked")  # Logging for debugging

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
            Input("close-modal", "n_clicks"),
        ],
        [State("login-state", "data")],
    )
    def handle_account_and_close(n_account, n_close, login_state):
        """Handles button clicks for account and modal close actions."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update, dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "account-button":
            return True, dash.no_update
        elif triggered_id == "close-modal":
            return False, dash.no_update

        return dash.no_update, dash.no_update

    # Callback separato per l'emoji di login

    @app.callback(
        [
            Output("login-indicator", "children"),
            Output("login-indicator", "style")
        ],
        [
            Input("login-state", "data"),
            Input("url", "pathname")  # Add URL pathname as input
        ],
    )
    def update_login_indicator(login_state, pathname):
        """Updates the login indicator emoji based on login state."""
        emoji = "👤" if login_state else "👻"
        print(f"Login state: {login_state}")
        return emoji, LOGIN_INDICATOR_STYLE

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
        start_year = start_year or 1990
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
            dati_scalati = pct_change * df['Percentuale'].values / 100

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

            warnings_data_string = f"L'analisi inizia dal {warnings_data[0]} sull'indice più recente: {warnings_data[1]}"

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


    def calculate_rolling_returns(portfolio_df, period):
        rolling_returns = portfolio_df.copy()
        rolling_returns = rolling_returns.set_index('Date')
        rolling_returns = rolling_returns.pct_change().rolling(window=period).sum()
        rolling_returns = rolling_returns.dropna()
        rolling_returns = rolling_returns.reset_index()
        return rolling_returns
    def add_rolling_traces(portfolio_df, period, PORTFOLIO_COLOR,column_except_date):
        if(len(portfolio_df) < period):
            rolling = go.Figure()
            return rolling.add_trace(go.Scatter(x=[0], y=[0], mode='text', text=f'Non ci sono abbastanza dati per calcolare i rendimenti rolling per {period} mesi'))
        else:
            rolling_returns = calculate_rolling_returns(portfolio_df, period)
            return plc.plot_line_chart_rolling(column_except_date, rolling_returns, PORTFOLIO_COLOR, BENCHMARK_COLOR,period)


    @app.callback(
        Output('additional-feedback', 'children'),  # Output to display the charts
        [Input('portfolio-data', 'data'),
         Input('assets-data', 'data'),
         Input('pesi-correnti', 'data')]
    )
    def plot_data(portfolio_data, dati,pesi_correnti):  # ----------- KING

        portfolio_df = pd.DataFrame(portfolio_data)
        dati_df = pd.DataFrame(dati) #Sto ricevendo un DICT e non un DataFrame, quindi le colonne duplicate erano state rimosse
        # Questo vuol dire che se metto due ETF uguali nella lista, uno dei due verrà rimosso

        # Ensure 'Date' column is datetime for calculations
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])

        rolling_periods = [36, 60, 120]

        column_except_date = [col for col in portfolio_df.columns if col != 'Date']

        rolling1 = add_rolling_traces(portfolio_df, rolling_periods[0], PORTFOLIO_COLOR,column_except_date)
        rolling2 = add_rolling_traces(portfolio_df, rolling_periods[1], PORTFOLIO_COLOR,column_except_date)
        rolling3 = add_rolling_traces(portfolio_df, rolling_periods[2], PORTFOLIO_COLOR,column_except_date)

        drawdown = plc.plot_drawdown(portfolio_df, PORTFOLIO_COLOR,BENCHMARK_COLOR,column_except_date)

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
        scatter_fig,pie_fig = ef.calcola_frontiera_efficente(dati_df,pesi_correnti) # TODO non plottare gli indici ma i nomi degli etf

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
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])
        ))
        volatility_fig.update_layout(
            title="Volatilità per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Volatilità (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        portfolio_fig = plc.plot_line_chart(column_except_date, portfolio_df, PORTFOLIO_COLOR, BENCHMARK_COLOR)

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

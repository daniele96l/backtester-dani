import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash.dash_table

# Costanti
FILE_PATH = "/Users/danieleligato/PycharmProjects/DaniBacktester/data/Index_list.csv"  # Assicurati che questo CSV sia nella stessa directory dello script
APP_TITLE = "PortfolioPilot"


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
    """Definisce il layout dell'app Dash utilizzando componenti Bootstrap."""
    return html.Div([
        # Header Container - Occupa tutta la larghezza dello schermo
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    html.H1(APP_TITLE, className='text-center my-4', style={'color': '#000000'}),
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
                    dbc.Label("Seleziona un ETF:", style={'color': '#000000'}),
                    dcc.Dropdown(
                        id='etf-dropdown',
                        options=[{'label': etf, 'value': etf} for etf in asset_list],
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
                        tooltip={"placement": "bottom", "always_visible": False},
                        updatemode='drag',
                    ),
                    html.Div(id='slider-value', className='text-center mt-2', style={'color': '#000000'})
                ], md=6),
            ], className='mb-4'),


            # Pulsante Aggiungi ETF
            dbc.Row(
                dbc.Col(
                    dbc.Button("Aggiungi ETF", id='add-etf-button', color='danger', className='w-100',
                               style={'backgroundColor': '#FA8072', 'borderColor': '#FA8072'}),
                    width=2
                ),
                className='mb-4'
            ),

            # Dropdown per il Benchmark
            dbc.Row([
                dbc.Col([
                    dbc.Label("Scegli il tuo Benchmark (Opzionale):", style={'color': '#000000'}),
                    dcc.Dropdown(
                        id='benchmark-dropdown',
                        options=[{'label': etf, 'value': etf} for etf in asset_list],
                        placeholder="Seleziona un Benchmark",
                        className='mb-3',
                        style={'backgroundColor': '#FFFFFF', 'color': '#000000'}
                    )
                ], md=6),
            ], className='mb-4'),

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
                )
            ),

            # Pulsante Crea Portafoglio
            dbc.Row(
                dbc.Col(
                    dbc.Button("Crea Portafoglio", id='create-portfolio-button', color='warning', className='w-100 mt-4',
                               style={'backgroundColor': '#8B4513', 'borderColor': '#8B4513'}),
                    width=2
                )
            ),

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
            # Div per Feedback Aggiuntivo
            dbc.Row([
                dbc.Col(
                    html.Div(id='additional-feedback', className='mt-2 text-center',
                             style={'fontSize': '1.1em', 'color': '#0000FF'}),  # Colore blu per esempio
                    width=12
                )
            ]),
        ], className='px-4', style={'backgroundColor': '#FFFFFF'})  # Container con margini orizzontali
    ])


def register_callbacks(app):
    """Registra tutti i callback per l'app Dash."""

    # Visualizza il valore corrente dello slider
    @app.callback(
        Output('slider-value', 'children'),
        [Input('percentage-slider', 'value')]
    )
    def display_slider_value(value):
        if value is None:
            value = 0  # Valore predefinito se lo slider non è impostato
        return f"Percentuale Selezionata: {value}%"

    # Callback per aggiungere un ETF alla tabella con la percentuale selezionata
    @app.callback(
        Output('portfolio-table', 'data'),
        [Input('add-etf-button', 'n_clicks')],
        [State('etf-dropdown', 'value'),
         State('percentage-slider', 'value'),
         State('portfolio-table', 'data')]
    )
    def add_etf_to_table(n_clicks, selected_etf, selected_percentage, current_data):
        if n_clicks is None:
            # Nessun clic ancora, restituisce i dati correnti invariati
            return current_data

        if n_clicks > 0:
            if not selected_etf:
                return current_data  # Nessun ETF selezionato, nessun cambiamento

            # Assicurati che current_data sia una lista di dizionari (righe della tabella)
            if current_data is None:
                current_data = []

            # Converti in DataFrame per una manipolazione più semplice
            current_df = pd.DataFrame(current_data)

            # Controlla se l'ETF esiste già nella tabella
            if 'ETF' in current_df.columns and not current_df[current_df['ETF'] == selected_etf].empty:
                return current_data  # Non aggiungere ETF duplicati

            # Assicurati che selected_percentage non sia None
            if selected_percentage is None:
                selected_percentage = 0

            # Controlla se l'aggiunta della nuova percentuale supera il 100%
            total_allocated = current_df['Percentuale'].sum() if not current_df.empty else 0
            if total_allocated + selected_percentage > 100:
                # Opzionalmente, puoi fornire un feedback all'utente qui
                return current_data

            # Aggiungi il nuovo ETF alla tabella
            new_row = {
                "ETF": selected_etf,
                "Percentuale": selected_percentage,
            }
            current_data.append(new_row)  # Aggiungi la nuova riga ai dati della tabella

        return current_data

    # Callback per verificare l'allocazione totale e fornire feedback
    @app.callback(
        Output('allocation-summary', 'children'),
        [Input('portfolio-table', 'data')]
    )
    def validate_allocation(table_data):
        if not table_data:
            return "Nessun ETF nel portafoglio al momento."

        # Somma le percentuali, gestendo valori mancanti o non validi
        try:
            total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
        except (ValueError, TypeError):
            return "Errore: Valore percentuale non valido rilevato."

        if total_percentage > 100:
            return f"Avviso: L'allocazione totale supera il 100% di {total_percentage - 100:.2f}%."
        elif total_percentage == 100:
            return "Successo: L'allocazione totale è esattamente del 100%."
        else:
            remaining = 100 - total_percentage
            return f"Allocazione totale: {total_percentage:.2f}%. Puoi allocare ancora {remaining:.2f}%."

    # Callback per gestire la creazione del portafoglio
    @app.callback(
        [Output('portfolio-feedback', 'children'),
         Output('portfolio-data', 'data'),
         Output('assets-data','data')],  # Aggiungi questo output
        [Input('create-portfolio-button', 'n_clicks')],
        [State('portfolio-table', 'data'),
         State('benchmark-dropdown', 'value')]  # Ottieni il benchmark selezionato
    )
    def create_portfolio(n_clicks, table_data, benchmark):
        if n_clicks is None:
            return "", dash.no_update,  dash.no_update

        if n_clicks > 0:
            if not table_data:
                return "Errore: Nessun ETF nel portafoglio da creare.", dash.no_update, dash.no_update

            # Calcola l'allocazione totale
            try:
                total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
            except (ValueError, TypeError):
                return "Errore: Valore percentuale non valido rilevato.", dash.no_update, dash.no_update

            if total_percentage != 100:
                return f"Errore: L'allocazione totale deve essere esattamente del 100%. Totale attuale: {total_percentage:.2f}%.", dash.no_update, dash.no_update

            # Converti i dati della tabella in DataFrame
            df = pd.DataFrame(table_data)

            # Stampa il portafoglio nel terminale del server
            print("=== Portafoglio Creato ===")
            print(df.to_string(index=False))
            print("===========================")

            indici = match_asset_name(df['ETF'])
            print("=== Indici corrispondenti ===")
            print(indici)
            print("=============================")

            dati = importa_dati(indici)
            if benchmark:
                indice_benchmark = match_asset_name([benchmark])
                dati_benckmark = importa_dati(indice_benchmark)

            dati_normalizzati = dati.copy()

            for i in range(len(dati.columns)):
                dati_normalizzati[dati.columns[i]] = dati[dati.columns[i]] * df['Percentuale'][i]

            #Somma delle colonne per trovare il valore del portafoglio
            dati_normalizzati['Portfolio'] = dati_normalizzati.sum(axis=1)
            dati_normalizzati = dati_normalizzati.drop(dati.columns, axis=1)

            portfolio_con_benchmark = dati_normalizzati.copy()

            if benchmark:
                #Join dei dati del portafoglio con quelli del benchmark
                portfolio_con_benchmark = dati_normalizzati.join(dati_benckmark[indice_benchmark[0]], how='inner', rsuffix='_benchmark')
                portfolio_con_benchmark['Benchmark'] = portfolio_con_benchmark[indice_benchmark[0]] / portfolio_con_benchmark[indice_benchmark[0]].iloc[0] * 100
                portfolio_con_benchmark = portfolio_con_benchmark.drop(columns=[indice_benchmark[0]])
                portfolio_con_benchmark['Portfolio'] = portfolio_con_benchmark['Portfolio'] / portfolio_con_benchmark['Portfolio'].iloc[0] * 100

            print("=== Dati Normalizzati con Benchmark ===")
            print(portfolio_con_benchmark)

            # Fornisci feedback all'utente e salva i dati nel Store
            return "Portafoglio creato con successo! Controlla la console del server per i dettagli.", portfolio_con_benchmark.to_dict('records'), dati_normalizzati.to_dict('records')

        return "", "",""

    # Callback per elaborare i dati del portafoglio e fornire feedback aggiuntivo
    def match_asset_name(nomi_assets):
        mapping = pd.read_csv(FILE_PATH)
        nomi_indici = mapping[mapping['Fund'].isin(nomi_assets)]['Index'].tolist()
        return nomi_indici

    def importa_dati(nomi_indici):
        dati = None  # Initialize an empty dataframe for merging
        for i in nomi_indici:
            # Read the data and set Date as the index
            temp_data = pd.read_csv(
                f"/Users/danieleligato/PycharmProjects/DaniBacktester/data/ETFs/{i}.csv",
                parse_dates=['Date']
            ).set_index('Date')

            if dati is None:
                dati = temp_data  # For the first dataframe, initialize `dati`
            else:
                dati = pd.concat([dati, temp_data], axis=1)  # Concatenate on index (Date)

        dati.dropna(inplace=True)  # Drop rows with missing values
        #Normalize all the columns making them start from 100
        dati = dati / dati.iloc[0] * 100

        return dati
    @app.callback(
        Output('additional-feedback', 'children'),  # Aggiungi un nuovo elemento nel layout per mostrare i risultati
        [Input('portfolio-data', 'data'),
         Input('assets-data', 'data')]
    )
    def elaborate_portfolio_data(portfolio_data, assets_data):
        print("=== Elaborazione dei Dati del Portafoglio ===")
        print(portfolio_data)
        print("=============================================")
        print("=== Dati degli Asset Importati ===")
        print(assets_data)

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
    app.run_server(debug=True)


if __name__ == '__main__':
    main()

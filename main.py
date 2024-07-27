import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Dashboard del Portfolio'),
    html.Div([
        dcc.Input(id='ticker-input', type='text', placeholder='Inserisci un simbolo ticker'),
        dcc.Input(id='percentage-input', type='number', placeholder='Percentuale', min=0, max=100, step=1),
        html.Button('Aggiungi', id='add-button', n_clicks=0),
    ]),
    dash_table.DataTable(
        id='portfolio-table',
        columns=[
            {'name': 'Ticker', 'id': 'ticker'},
            {'name': 'Percentuale', 'id': 'percentage'},
        ],
        data=[],
        row_selectable='single',
        selected_rows=[],
    ),
    html.Button('Rimuovi Selezionato', id='remove-button', n_clicks=0),
    html.Div(id='percentage-warning', style={'color': 'red', 'margin-top': '10px'}),
    dcc.Graph(id='portfolio-graph')
])


@app.callback(
    [Output('portfolio-table', 'data'),
     Output('ticker-input', 'value'),
     Output('percentage-input', 'value'),
     Output('portfolio-table', 'selected_rows'),
     Output('percentage-warning', 'children')],
    [Input('add-button', 'n_clicks'),
     Input('remove-button', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('percentage-input', 'value'),
     State('portfolio-table', 'data'),
     State('portfolio-table', 'selected_rows')]
)
def update_portfolio(add_clicks, remove_clicks, ticker, percentage, rows, selected_rows):
    ctx = dash.callback_context
    if not ctx.triggered:
        return rows, '', None, [], ''

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-button' and ticker and percentage:
        rows.append({'ticker': ticker.upper(), 'percentage': percentage})
    elif button_id == 'remove-button' and selected_rows:
        rows = [row for i, row in enumerate(rows) if i not in selected_rows]

    total_percentage = sum(float(row['percentage']) for row in rows)
    warning = ''
    if total_percentage != 100:
        warning = f'Attenzione: La somma delle percentuali è {total_percentage}%, non 100%'

    return rows, '', None, [], warning


@app.callback(
    Output('portfolio-graph', 'figure'),
    Input('portfolio-table', 'data')
)
def update_graph(rows):
    if not rows:
        return go.Figure()

    end_date = pd.Timestamp.now()

    # Scarichiamo i dati per tutti gli asset
    data_dict = {}
    for row in rows:
        ticker = row['ticker']
        data = yf.download(ticker, start='1900-01-01', end=end_date)
        data_dict[ticker] = data['Close']

    # Troviamo la prima data in comune
    common_dates = pd.concat(data_dict.values(), axis=1).dropna().index
    if len(common_dates) == 0:
        return go.Figure()  # Non ci sono date in comune
    start_date = common_dates[0]

    fig = go.Figure()

    portfolio_value = pd.Series(0, index=common_dates)
    total_percentage = 0

    for row in rows:
        ticker = row['ticker']
        percentage = float(row['percentage'])
        total_percentage += percentage
        data = data_dict[ticker][start_date:]

        # Normalizza i prezzi al valore iniziale (valore assoluto normalizzato)
        normalized_price = data / data.iloc[0]

        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized_price,
            name=f"{ticker} ({percentage}%)",
            mode='lines'
        ))

        # Calcola il contributo pesato al valore totale del portfolio
        portfolio_value += normalized_price * (percentage / 100)

    # Aggiungi la linea del valore totale del portfolio se la somma delle percentuali è 100%
    if abs(total_percentage - 100) < 0.001:  # Usiamo una piccola tolleranza per gli errori di arrotondamento
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value,
            name='Valore Totale Portfolio',
            mode='lines',
            line=dict(color='black', width=2, dash='dash')
        ))

    fig.update_layout(
        title=f'Andamento dei Componenti del Portfolio (dal {start_date.strftime("%Y-%m-%d")})',
        xaxis_title='Data',
        yaxis_title='Valore Normalizzato',
        legend_title='Titoli'
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date, datetime
import numpy as np

app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'])

app.layout = html.Div([
    html.H1('Dashboard del Portfolio', style={'textAlign': 'center'}),
    html.Div([
        dcc.Input(id='ticker-input', type='text', placeholder='Inserisci un simbolo ticker', style={'marginRight': '10px'}),
        dcc.Input(id='percentage-input', type='number', placeholder='Percentuale', min=0, max=100, step=1, style={'marginRight': '10px'}),
        html.Button('Aggiungi', id='add-button', n_clicks=0),
    ], style={'marginBottom': '20px'}),
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='portfolio-table',
                columns=[
                    {'name': 'Ticker', 'id': 'ticker'},
                    {'name': 'Percentuale', 'id': 'percentage'},
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'backgroundColor': '#2C2C2C',
                    'color': '#FFFFFF',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': '#3C3C3C',
                    'fontWeight': 'bold'
                }
            ),
            html.Button('Rimuovi Selezionato', id='remove-button', n_clicks=0, style={'marginTop': '10px'}),
            html.Div(id='percentage-warning', style={'color': 'red', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Input(id='benchmark-input', type='text', placeholder='Inserisci un simbolo benchmark', style={'marginRight': '10px'}),
            html.Button('Cambia Benchmark', id='add-benchmark-button', n_clicks=0),
            dash_table.DataTable(
                id='benchmark-table',
                columns=[
                    {'name': 'Benchmark', 'id': 'benchmark'},
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'backgroundColor': '#2C2C2C',
                    'color': '#FFFFFF',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': '#3C3C3C',
                    'fontWeight': 'bold'
                }
            ),
            html.Button('Rimuovi Benchmark Selezionato', id='remove-benchmark-button', n_clicks=0, style={'marginTop': '10px'}),
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    html.Div([
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date(date.today().year - 1, date.today().month, date.today().day),
            style={'marginRight': '10px'}
        ),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date.today()
        ),
    ], style={'marginTop': '20px', 'marginBottom': '20px'}),
    dcc.Graph(id='portfolio-graph'),
    html.Button('Calcola Efficient Frontier', id='efficient-frontier-button', n_clicks=0, style={'marginTop': '20px'}),
    dcc.Graph(id='efficient-frontier-graph'),
    dcc.Graph(id='optimal-portfolio-performance-graph'),
    html.Div(id='pie-charts', style={'display': 'flex', 'justifyContent': 'space-between'}),
    dcc.Graph(id='comparison-chart')

], style={'padding': '20px'})



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
    [Output('benchmark-table', 'data'),
     Output('benchmark-input', 'value'),
     Output('benchmark-table', 'selected_rows')],
    [Input('add-benchmark-button', 'n_clicks')],
    [State('benchmark-input', 'value'),
     State('benchmark-table', 'data')]
)
def update_benchmark(n_clicks, benchmark, rows):
    if n_clicks > 0 and benchmark:
        rows = [{'benchmark': benchmark.upper()}]
    return rows, '', []




@app.callback(
    Output('portfolio-graph', 'figure'),
    [Input('portfolio-table', 'data'),
     Input('benchmark-table', 'data'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def update_graph(rows, benchmark_rows, start_date, end_date):
    if not rows or not start_date or not end_date:
        return go.Figure()

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Scarichiamo i dati per tutti gli asset
    data_dict = {}
    for row in rows:
        ticker = row['ticker']
        data = yf.download(ticker, start=start_date, end=end_date)
        data_dict[ticker] = data['Close']

    # Scarichiamo i dati per il benchmark
    if not benchmark_rows:
        benchmark_rows = [{'benchmark': '^GSPC'}]  # Default to S&P 500 if no benchmark is selected

    # Scarichiamo i dati per il benchmark
    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = yf.download(benchmark, start=start_date, end=end_date)
        data_dict[benchmark] = data['Close']

    # Troviamo la prima data in comune
    common_dates = pd.concat(data_dict.values(), axis=1).dropna().index
    if len(common_dates) == 0:
        return go.Figure()  # Non ci sono date in comune

    fig = go.Figure()

    portfolio_value = pd.Series(0, index=common_dates)
    total_percentage = 0

    for row in rows:
        ticker = row['ticker']
        percentage = float(row['percentage'])
        total_percentage += percentage
        data = data_dict[ticker]

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
            line=dict(color='white', width=2, dash='dash')
        ))

    # Aggiungi i benchmark
    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = data_dict[benchmark]
        normalized_price = data / data.iloc[0]

        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized_price,
            name=f"Benchmark: {benchmark}",
            mode='lines',
            line=dict(dash='dot')
        ))

    fig.update_layout(
        title=f'Andamento dei Componenti del Portfolio e Benchmark (dal {common_dates[0].strftime("%Y-%m-%d")} al {common_dates[-1].strftime("%Y-%m-%d")})',
        xaxis_title='Data',
        yaxis_title='Valore Normalizzato',
        legend_title='Titoli',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig

@app.callback(
    [Output('efficient-frontier-graph', 'figure'),
     Output('optimal-portfolio-performance-graph', 'figure'),
     Output('pie-charts', 'children'),
     Output('comparison-chart', 'figure')],
    [Input('efficient-frontier-button', 'n_clicks')],
    [State('portfolio-table', 'data'),
     State('benchmark-table', 'data'),
     State('start-date-picker', 'date'),
     State('end-date-picker', 'date')]
)
def calculate_efficient_frontier(n_clicks, rows, benchmark_rows, start_date, end_date):
    if not rows or not start_date or not end_date or n_clicks == 0:
        # Restituisci figure vuote e liste vuote se non ci sono dati
        empty_fig = go.Figure()
        return empty_fig, empty_fig, [], empty_fig

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Scarichiamo i dati per tutti gli asset
    data_dict = {}
    for row in rows:
        ticker = row['ticker']
        data = yf.download(ticker, start=start_date, end=end_date)
        data_dict[ticker] = data['Close']


    # Scarichiamo i dati per il benchmark
    if not benchmark_rows:
        benchmark_rows = [{'benchmark': '^GSPC'}]

    # Scarichiamo i dati per il benchmark
    benchmark_data = {}
    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = yf.download(benchmark, start=start_date, end=end_date)
        benchmark_data[benchmark] = data['Close']

    # Troviamo la prima data in comune
    common_data = pd.concat(data_dict.values(), axis=1).dropna()
    if common_data.empty:
        return go.Figure()  # Non ci sono date in comune

    common_data.columns = [row['ticker'] for row in rows]
    returns = common_data.pct_change().dropna()

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_portfolios = 10000
    results = np.zeros((4, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(len(rows))
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_return = np.dot(weights, mean_returns) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        results[2,i] = results[0,i] / results[1,i]
        results[3,i] = np.dot(weights, mean_returns)

    max_sharpe_idx = np.argmax(results[2])
    min_std_dev_idx = np.argmin(results[1])
    max_return_idx = np.argmax(results[0])

    # Calculate the current portfolio return and std dev
    current_weights = np.array([float(row['percentage']) / 100 for row in rows])
    current_return = np.dot(current_weights, mean_returns) * 252
    current_std_dev = np.sqrt(np.dot(current_weights.T, np.dot(cov_matrix, current_weights))) * np.sqrt(252)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=results[1],
        y=results[0],
        mode='markers',
        marker=dict(
            color=results[2],
            colorscale='Viridis',
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        )
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,max_sharpe_idx]],
        y=[results[0,max_sharpe_idx]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='diamond'),
        name='Max Sharpe Ratio'
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,min_std_dev_idx]],
        y=[results[0,min_std_dev_idx]],
        mode='markers',
        marker=dict(color='blue', size=10, symbol='diamond'),
        name='Min Volatility'
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,max_return_idx]],
        y=[results[0,max_return_idx]],
        mode='markers',
        marker=dict(color='green', size=10, symbol='diamond'),
        name='Max Return'
    ))

    fig.add_trace(go.Scatter(
        x=[current_std_dev],
        y=[current_return],
        mode='markers',
        marker=dict(color='magenta', size=10, symbol='diamond'),
        name='Current Portfolio'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Rischio/Volatilità',
        yaxis_title='Ritorno',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    max_sharpe_weights = weights_record[max_sharpe_idx]
    min_vol_weights = weights_record[min_std_dev_idx]
    max_return_weights = weights_record[max_return_idx]
    current_weights = np.array([float(row['percentage']) / 100 for row in rows])

    ef_fig = create_efficient_frontier_graph(results, max_sharpe_idx, min_std_dev_idx, max_return_idx, current_std_dev,
                                             current_return)
    perf_fig = create_optimal_portfolio_performance_graph(common_data, max_sharpe_weights, min_vol_weights,
                                                          max_return_weights, current_weights, rows, benchmark_data)

    pie_charts = create_pie_charts(rows, max_sharpe_weights, min_vol_weights, max_return_weights, current_weights)

    portfolio_data = {}
    portfolios = {
        'Max Sharpe': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights,
        'Current Portfolio': current_weights
    }

    risk_free_rate = 0.02  # Assume a 2% risk-free rate, you may want to make this dynamic

    for name, weights in portfolios.items():
        portfolio_return = (common_data * weights).sum(axis=1)
        cagr = calculate_cagr(portfolio_return)
        annualized_volatility = calculate_annualized_volatility(portfolio_return)
        annualized_down_volatility = calculate_annualized_down_volatility(portfolio_return)
        sharpe_ratio = (cagr - risk_free_rate) / annualized_volatility
        portfolio_data[name] = {'CAGR': cagr, 'Volatility': annualized_volatility, 'Sharpe Ratio': sharpe_ratio, 'Downside Volatility': annualized_down_volatility}

    # Calculate CAGR, Volatility, and Sharpe Ratio for the benchmark
    benchmark_name = benchmark_rows[0]['benchmark']  # Assume there's only one benchmark
    benchmark_return = benchmark_data[benchmark_name]
    benchmark_cagr = calculate_cagr(benchmark_return)
    benchmark_volatility = calculate_annualized_volatility(benchmark_return)
    benchmark_down_volatility = calculate_annualized_down_volatility(benchmark_return)
    benchmark_sharpe_ratio = (benchmark_cagr - risk_free_rate) / benchmark_volatility
    benchmark_data = {
        'CAGR': benchmark_cagr,
        'Volatility': benchmark_volatility,
        'Sharpe Ratio': benchmark_sharpe_ratio,
        'Downside Volatility': benchmark_down_volatility
    }

    comparison_fig = create_comparison_chart(portfolio_data, benchmark_data)

    return ef_fig, perf_fig, pie_charts, comparison_fig

def calculate_cagr(data):
    start_value = data.iloc[0]
    end_value = data.iloc[-1]
    n_years = len(data) / 252  # Assumendo 252 giorni di trading all'anno
    cagr = (end_value / start_value) ** (1 / n_years) - 1
    return cagr

def calculate_annualized_volatility(returns):
    """
    Calcola la volatilità annualizzata dei ritorni annualizzati.
    """
    annual_returns = returns.resample('Y').last().pct_change().dropna()
    annual_volatility = annual_returns.std()
    return annual_volatility

def calculate_annualized_down_volatility(returns):
    """
    Calcola la volatilità annualizzata dei ritorni annualizzati.
    """
    annual_returns = returns.resample('Y').last().pct_change().dropna()
    #Rimuovi i rendimenti positivi
    annual_returns = annual_returns[annual_returns < 0]
    annual_volatility = annual_returns.std()
    return annual_volatility


def create_comparison_chart(portfolio_data, benchmark_data):
    portfolios = list(portfolio_data.keys()) + ['Benchmark']
    metrics = ['CAGR', 'Volatility', 'Sharpe Ratio', 'Downside Volatility']

    # Definiamo colori diversi per ogni portfolio e il benchmark
    colors = ['red', 'blue', 'green', 'purple', 'orange']  # Add a color for the benchmark

    fig = go.Figure()

    for i, portfolio in enumerate(portfolios):
        data = portfolio_data[portfolio] if portfolio != 'Benchmark' else benchmark_data
        for metric in metrics:
            fig.add_trace(go.Bar(
                name=portfolio,
                x=[metric],
                y=[data[metric]],
                marker_color=colors[i % len(colors)],
                showlegend=True if metric == 'CAGR' else False
            ))

    fig.update_layout(
        title='Confronto CAGR, Volatilità e Sharpe Ratio (incluso Benchmark)',
        barmode='group',
        xaxis_title='Metriche',
        yaxis_title='Valore',
        legend_title='Portafogli',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig

def create_pie_charts(rows, max_sharpe_weights, min_vol_weights, max_return_weights, current_weights):
    tickers = [row['ticker'] for row in rows]

    pie_charts = []
    portfolios = {
        'Current Portfolio': current_weights,
        'Max Sharpe Ratio': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights
    }

    for name, weights in portfolios.items():
        pie = dcc.Graph(
            figure=go.Figure(data=[go.Pie(
                labels=tickers,
                values=weights,
                textinfo='label+percent',
                insidetextorientation='radial'
            )]),
            style={'width': '25%', 'display': 'inline-block'},
            config={'displayModeBar': False}
        )
        pie.figure.update_layout(
            title=name,
            paper_bgcolor='#1E1E1E',
            plot_bgcolor='#1E1E1E',
            font=dict(color='#FFFFFF')
        )
        pie_charts.append(pie)

    return pie_charts


def create_efficient_frontier_graph(results, max_sharpe_idx, min_std_dev_idx, max_return_idx, current_std_dev, current_return):
    fig = go.Figure()

    # Scatter plot per tutti i portafogli
    fig.add_trace(go.Scatter(
        x=results[1],
        y=results[0],
        mode='markers',
        marker=dict(
            color=results[2],
            colorscale='Viridis',
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        ),
        name='Portafogli'
    ))

    # Punto per il portafoglio con massimo Sharpe Ratio
    fig.add_trace(go.Scatter(
        x=[results[1,max_sharpe_idx]],
        y=[results[0,max_sharpe_idx]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='diamond'),
        name='Max Sharpe Ratio'
    ))

    # Punto per il portafoglio con minima volatilità
    fig.add_trace(go.Scatter(
        x=[results[1,min_std_dev_idx]],
        y=[results[0,min_std_dev_idx]],
        mode='markers',
        marker=dict(color='blue', size=10, symbol='diamond'),
        name='Min Volatility'
    ))

    # Punto per il portafoglio con massimo ritorno
    fig.add_trace(go.Scatter(
        x=[results[1,max_return_idx]],
        y=[results[0,max_return_idx]],
        mode='markers',
        marker=dict(color='green', size=10, symbol='diamond'),
        name='Max Return'
    ))

    # Punto per il portafoglio corrente
    fig.add_trace(go.Scatter(
        x=[current_std_dev],
        y=[current_return],
        mode='markers',
        marker=dict(color='magenta', size=10, symbol='diamond'),
        name='Current Portfolio'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Rischio/Volatilità',
        yaxis_title='Ritorno',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig

def create_optimal_portfolio_performance_graph(data, max_sharpe_weights, min_vol_weights, max_return_weights, current_weights, rows, benchmark_data):
    fig = go.Figure()

    # Calcola le performance dei portafogli ottimali
    portfolios = {
        'Max Sharpe': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights,
        'Current Portfolio': current_weights
    }

    for name, weights in portfolios.items():
        portfolio_return = (data * weights).sum(axis=1)
        normalized_return = portfolio_return / portfolio_return.iloc[0]
        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized_return,
            mode='lines',
            name=name
        ))

    # Aggiungi i benchmark
    for benchmark, benchmark_prices in benchmark_data.items():
        normalized_benchmark = benchmark_prices / benchmark_prices.iloc[0]
        fig.add_trace(go.Scatter(
            x=normalized_benchmark.index,
            y=normalized_benchmark,
            mode='lines',
            name=f'Benchmark: {benchmark}',
            line=dict(dash='dash')
        ))

    fig.update_layout(
        title='Performance dei Portafogli Ottimali e Benchmark',
        xaxis_title='Data',
        yaxis_title='Valore Normalizzato',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

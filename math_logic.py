import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.colors as pc
#plc
from plotly.subplots import make_subplots
from plotly import graph_objs as go
from Frontend import plot_line_chart as plc

from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, INDEX_LIST_FILE_PATH
class MathLogic:
    def add_rolling_traces(portfolio_df, period,column_except_date):
        if(len(portfolio_df) < period):
            rolling = go.Figure()
            return rolling.add_trace(go.Scatter(x=[0], y=[0], mode='text', text=f'Non ci sono abbastanza dati per calcolare i rendimenti rolling per {period} mesi'))
        else:
            rolling_returns = MathLogic.calculate_rolling_returns(portfolio_df, period)
            return plc.plot_line_chart_rolling(column_except_date, rolling_returns, PORTFOLIO_COLOR, BENCHMARK_COLOR,period)


    def calculate_rolling_returns(portfolio_df, period):
        rolling_returns = portfolio_df.copy()
        rolling_returns = rolling_returns.set_index('Date')
        rolling_returns = rolling_returns.pct_change().rolling(window=period).sum()
        rolling_returns = rolling_returns.dropna()
        rolling_returns = rolling_returns.reset_index()
        return rolling_returns

    def calculate_performance_metrics(portfolio_df, portfolio_returns, column_except_date):
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
        #ig cagr is longer than 2 columns, it means that the benchmark is present, so we need to adjust the values
        #BAD BAD BAD CODE
        if len(cagr) >= 2:
            diff = cagr['Portfolio'] - portfolio_returns* 100
            cagr['Portfolio'] = portfolio_returns * 100
            cagr["Benchmark"] = cagr['Benchmark'] - diff
        else:
            cagr['Portfolio'] = portfolio_returns * 100

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
        return cagr_data, volatility_data, sharpe_data


    def calculate_3_rolling_returns(portfolio_df, rolling_periods,column_except_date):
        rolling1 = MathLogic.add_rolling_traces(portfolio_df, rolling_periods[0],column_except_date)
        rolling2 = MathLogic.add_rolling_traces(portfolio_df, rolling_periods[1],column_except_date)
        rolling3 = MathLogic.add_rolling_traces(portfolio_df, rolling_periods[2],column_except_date)
        return rolling1, rolling2, rolling3


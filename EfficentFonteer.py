import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Define colors for benchmark and portfolio
benchmark_color = 'rgba(250, 128, 114, 0.7)'
portfolio_color = 'rgba(135, 206, 250, 0.7)'

custom_colorscale = [
    [0, benchmark_color],    # Start of the scale
    [1, portfolio_color]     # End of the scale
]

def calcola_frontiera_efficente(dati): # TODO non plottare gli indici ma i nomi degli etf
    if dati is None or dati.empty:
        raise ValueError("Input data is missing or empty.")

    # Copy data
    all_normalized_assets_ef = dati.copy()

    # Extract monthly returns for all columns
    monthly_returns = all_normalized_assets_ef.pct_change().dropna()
    symbols = monthly_returns.columns

    # Annualize returns
    annual_returns = (1 + monthly_returns).prod() ** (12 / len(monthly_returns)) - 1

    # Annualized covariance matrix
    cov_matrix = monthly_returns.cov() * 12

    # Monte Carlo simulation
    num_portfolios = 5000
    weights = np.random.random((num_portfolios, len(symbols)))
    weights /= weights.sum(axis=1, keepdims=True)

    # Portfolio metrics
    portfolio_returns = np.dot(weights, annual_returns)
    portfolio_std_devs = np.sqrt(np.einsum('ij,ji->i', weights.dot(cov_matrix), weights.T))
    risk_free_rate = 0.00
    sharpe_ratios = (portfolio_returns - risk_free_rate) / portfolio_std_devs

    # Key portfolios
    max_sharpe_idx = np.argmax(sharpe_ratios)
    min_std_dev_idx = np.argmin(portfolio_std_devs)
    max_return_idx = np.argmax(portfolio_returns)

    results_df = pd.DataFrame({
        'Annual Return': portfolio_returns,
        'Annual Volatility': portfolio_std_devs,
        'Sharpe Ratio': sharpe_ratios
    })

    for i, symbol in enumerate(symbols):
        results_df[f'{symbol} Weight'] = weights[:, i]

    # Key portfolios only
    key_portfolios = [
        results_df.iloc[max_sharpe_idx],
        results_df.iloc[min_std_dev_idx],
        results_df.iloc[max_return_idx]
    ]

    all_model_portfolios = pd.DataFrame(key_portfolios).reset_index(drop=True)
    all_model_portfolios['Portfolio'] = ['Max Sharpe', 'Min Volatility', 'Max Return']

    # Scatter Plot using Plotly
    scatter_fig = go.Figure()

    scatter_fig.add_trace(go.Scatter(
        x=results_df['Annual Volatility'],
        y=results_df['Annual Return'],
        mode='markers',
        marker=dict(
            color=results_df['Sharpe Ratio'],
            colorscale=custom_colorscale,
            showscale=True,
            size=5,
            opacity=0.5
        ),
        name='Portfolios'
    ))

    colors = ['red', 'blue', 'green']
    markers = ['circle', 'star', 'triangle-up']
    for i, (_, portfolio) in enumerate(all_model_portfolios.iterrows()):
        scatter_fig.add_trace(go.Scatter(
            x=[portfolio['Annual Volatility']],
            y=[portfolio['Annual Return']],
            mode='markers+text',
            marker=dict(
                size=12,
                color=colors[i],
                symbol=markers[i]
            ),
            text=[portfolio['Portfolio']],
            textposition='top center',
            name=portfolio['Portfolio']
        ))

    # Update layout to move the legend inside the figure
    scatter_fig.update_layout(
        title='Frontiera efficent dati gli asset selezionati',
        xaxis=dict(title='Volatilità Annuale (%)',
                   tickformat='.2%'  # Multiply by 100 and display with 2 decimal places
                   ),
        yaxis=dict(title='Ritorno Annuale (%)',
                   tickformat='.2%'  # Multiply by 100 and display with 2 decimal places

                   ),
        coloraxis_colorbar=dict(title='Sharpe Ratio'),
        showlegend=True,  # Enable legend
        legend=dict(
            x=0.8,  # Horizontal position inside the figure (e.g., 70% of width)
            y=0.6,  # Vertical position inside the figure (e.g., 20% of height)
            xanchor='left',  # Anchor legend by its left side
            yanchor='bottom',  # Anchor legend by its bottom side
            bgcolor='rgba(255, 255, 255, 0.8)',  # Optional: Add a semi-transparent white background
            bordercolor='black',  # Optional: Add a border for clarity
            borderwidth=1  # Optional: Set border width
        )
    )

    # Pie Charts for Asset Allocation using Plotly
    weight_columns = [col for col in all_model_portfolios.columns if 'Weight' in col]
    pie_fig = go.Figure()

    if weight_columns:
        all_assets = [col.replace(' Weight', '') for col in weight_columns]

        # Create a color mapping for each asset (using original asset names)
        pastel_colors = [
            "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
            "#FFC4C4", "#FFE4C4", "#FFFFC4", "#C4FFC9", "#C4E1FF",
            "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
            "#FFC4C4", "#FFE4C4", "#FFFFC4", "#C4FFC9", "#C4E1FF",
        ]
        asset_color_map = {asset: pastel_colors[i % len(pastel_colors)] for i, asset in enumerate(all_assets)}

        for i, (_, portfolio) in enumerate(all_model_portfolios.iterrows()):
            weights = portfolio[weight_columns]
            # Filter out positions smaller than 5%
            significant_weights = weights[weights >= 0.05]

            # Redistribute the weight of small positions
            if len(significant_weights) < len(weights):
                total_significant = significant_weights.sum()
                scaling_factor = 1 / total_significant
                significant_weights = significant_weights * scaling_factor

            # Get the original asset names (keys for asset_color_map)
            original_labels = significant_weights.index.str.replace(' Weight', '')

            # Modify labels for display (add <br> tags for long labels)
            display_labels = [str(label).replace(" ", "<br>") if len(str(label)) > 20 else str(label) for label in
                              original_labels]

            # Assign colors based on the original asset names
            colors = [asset_color_map[asset] for asset in original_labels]

            pie_fig.add_trace(go.Pie(
                labels=display_labels,  # Use modified labels for display
                values=significant_weights.values.astype(float).round(2),
                name=portfolio['Portfolio'],
                title=f"{portfolio['Portfolio']}<br>Ritorno: {portfolio['Annual Return']:.2%}<br>Volatilità: {portfolio['Annual Volatility']:.2%}<br>Sharpe: {portfolio['Sharpe Ratio']:.2f}",
                textinfo='label+percent',
                hoverinfo='label+value',
                marker=dict(colors=colors),  # Use colors mapped to original asset names
                domain=dict(row=i // 3, column=i % 3)
            ))

        pie_fig.update_layout(
            title='Portafogli Efficenti usando gli indici dei tuoi ETF',
            grid=dict(rows=1, columns=3, pattern="independent"),
        )

    else:
        pie_fig = None

    return scatter_fig, pie_fig
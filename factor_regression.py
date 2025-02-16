import pandas as pd
import statsmodels.api as sm
from config import DEV_FIVE_FACTORS_FILE_PATH


def import_fama_french():
    fama_french = pd.read_csv(f"{DEV_FIVE_FACTORS_FILE_PATH}", parse_dates=['Date'])
    fama_french = fama_french.set_index('Date')
    fama_french = fama_french / 100
    return fama_french
def calculate_factor_exposure(portfolio_df):
    # Calculate the percentage change (returns) and drop missing values
    portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
    portfolio_df.set_index('Date', inplace=True)

    # Calculate returns for the portfolio and rename the column to 'Adj Close'
    data = portfolio_df.pct_change().dropna()
    data["Adj Close"] = data  # Rename the column to 'Adj Close'

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
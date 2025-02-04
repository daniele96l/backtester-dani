from pathlib import Path

APP_TITLE = "PortfolioPilot"

# Define colors for benchmark and portfolio
BENCHMARK_COLOR = 'rgba(250, 128, 114, 0.7)'
PORTFOLIO_COLOR = 'rgba(135, 206, 250, 0.7)'

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 80

if Path("data").exists():
    # La cartella data è stata trovata nel path relativo (ambiente locale/dev)
    DATA_PATH = Path("data")
else:
    # La cartella data NON è stata trovata nel path relativo (ambiente prod)
    DATA_PATH = Path.home() / "backtester" / "backtester-dani" / "data"

INDEX_LIST_FILE_PATH = DATA_PATH / "Index_list_cleaned.csv"
ETF_BASE_PATH = DATA_PATH / "ETFs"
DEV_FIVE_FACTORS_FILE_PATH = DATA_PATH / "Developed_5_Factors.csv"
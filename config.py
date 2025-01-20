# config.py

# Paths and Constants
DEBUG = True
if DEBUG:
    FILE_PATH = "data/Index_list_cleaned.csv"  # Ensure this CSV is in the same directory as the script
    ETF_BASE_PATH = "data/ETFs"
    BASE_PATH = "data"
else:
    FILE_PATH = "/home/dani/backtester/backtester-dani/data/Index_list_cleaned.csv"
    ETF_BASE_PATH = "/home/dani/backtester/backtester-dani/data/ETFs"
    BASE_PATH = "/home/dani/backtester/backtester-dani/data"


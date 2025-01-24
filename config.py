import os
import platform

# Check if the operating system is macOS (local machine)
if platform.system() == 'Darwin':  # 'Darwin' is the name for macOS
    Local = True
else:
    Local = False

if Local:
    FILE_PATH = "data/Index_list_cleaned.csv"
    ETF_BASE_PATH = "data/ETFs"
    BASE_PATH = "data"
else:
    FILE_PATH = "/home/dani/backtester/backtester-dani/data/Index_list_cleaned.csv"
    ETF_BASE_PATH = "/home/dani/backtester/backtester-dani/data/ETFs"
    BASE_PATH = "/home/dani/backtester/backtester-dani/data"

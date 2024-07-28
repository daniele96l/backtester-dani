# downlaad apple data from yahoo fiannce
# and plot the data

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime

import yfinance as yf

# download apple data from yahoo finance
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime(2018, 12, 31)
apple = yf.download("AAPL", start=start, end=end)

# plot the data
plt.plot(apple['Close'])
plt.title('Apple stock price')

plt.show()

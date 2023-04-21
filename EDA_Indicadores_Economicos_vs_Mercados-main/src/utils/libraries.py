# Librerias a utilizar en el EDA

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from pandas_datareader import data as pdr
import yfinance as yfin
import datetime as dt
from datetime import datetime
import seaborn as sns
# Librería de la FRED
from fredapi import Fred
from IPython.display import display, HTML
from scipy.stats import pearsonr
import itertools
from scipy.stats import ttest_ind

# API Key
fred_key = '2e3cf97d1b456831253eda002ce25948'
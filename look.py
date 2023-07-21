import pandas as pd
import yfinance as yf
import pandas_ta as ta
from ha import HA

def abovebelow(row:pd.Series):
    if row['K'] >= 80:
        return 'A'
    elif row['K'] <= 20:
        return 'B'
    else:
        return 'I'

def redgreen(row:pd.Series):
    if row['open'] > row['close']:
        return 'R'
    elif row['open'] < row['close']:
        return 'G'
    else:
        return 'I'
    
tickers = list( pd.read_csv("tickers.txt", header=None)[0])

dfmo = yf.download(tickers=tickers, period='1mo', interval='1h', group_by='tickers')
# df.to_pickle('mo.pickle')
# dfmo = pd.read_pickle('mo.pickle')
dfwk = yf.download(tickers=tickers, period='5d', interval='15m', group_by='tickers')
# dfwk.to_pickle('wk.pickle')
# dfwk = pd.read_pickle('wk.pickle')

candidates = []
for ticker in tickers:
    stoch = dfmo[ticker].ta.stochrsi()
    stoch.columns = ['K', 'D']
    hawk = HA(dfwk[ticker])
    rg = hawk.apply(redgreen, axis=1, raw=False)[-1]
    ab = stoch.apply(abovebelow, axis=1, raw=False)[-1]
    
    match (ab, rg):
        case ('A', 'R'):
            candidates.append( f'{ticker:>6} SHORT {ab} {rg}')
        case ('B', 'G'):
            candidates.append( f'{ticker:>6} LONG  {ab} {rg}')
        case _:
            pass
for x in candidates:
    print(x)
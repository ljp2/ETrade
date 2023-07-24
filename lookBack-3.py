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
    
    
def longshort(df):
    c = df['color']
    match c[-3]:
        case 'R':
            if c[-2] == 'G' and c[-1] == 'G':
                return 'Long'
            elif c[-2] == 'R' and c[-1] == 'R':
                return 'DOWN'
            else:
                return 'X'        
        case 'G':
            if c[-2] == 'R' and c[-1] == 'R':
                return 'SHORT'
            elif c[-2] == 'G' and c[-1] == 'G':
                return 'UP'
            else:
                return 'X'    
        
        case 'I':
            return 'X'
        
    

tickers = list( pd.read_csv("tickers.txt", header=None)[0])
# dfwk = yf.download(tickers=tickers, period='5d', interval='1h', group_by='tickers')
# dfwk.to_pickle('wk.pickle')
dfwk = pd.read_pickle('wk.pickle')

long = []
short = []
for ticker in tickers:
    df = dfwk[ticker].copy()
    df.columns = df.columns.str.lower()
    df['color'] = df.apply(redgreen, axis=1)
    x = longshort(df)
    if x == 'LONG':
        long.append(f'{ticker:10}  {x}')
    if x == "SHORT":
        short.append(f'{ticker:10}  {x}')
    
for x in long:
    print(x)
print()
for x in short:
    print(x)


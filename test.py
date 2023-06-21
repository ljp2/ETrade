import pandas_ta as ta
import pandas as pd
import alpacaAPI as api

def crossovers(p1,p2):
    a = []
    high = True
    for i in range(len(p1)):
        if p1[i] is not None and p2[i] is not None:
            if high and p1[i] < p2[i]:
                a.append([i,2])
                high = False
            if not high and p1[i] > p2[i]:
                a.append([i,1])
                high = True
    return a



df = api.get_bars_dataframe('SPY', '1Week', '1Hr')
cols = list(df.columns)
df = df.tz_convert('US/Eastern')

sf = df.ta.stochrsi(append=True)
sf.columns = ['K', 'D']
sf.dropna(inplace=True)

lastabove = False
lastbelow = False
lastk = 0
lastd = 0
for i, row in sf.iterrows():
    k = row.K
    d = row.D   
    above = k>d
    below = not above
    crossup = above and lastbelow
    crossdwn = below and lastabove
    lastabove = above
    lastbelow = below
    if crossup:
        print(f'UP\t{lastk:.2f}\t{lastd:.2f}\t{k:.2f}\t{d:.2f}')
    if crossdwn:
        print(f'DWN\t{lastk:.2f}\t{lastd:.2f}\t{k:.2f}\t{d:.2f}')
    lastk = k
    lastd = d
    
    
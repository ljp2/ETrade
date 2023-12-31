def HA(df):
    df.columns = df.columns.str.lower()
    
    new_df = df[['open', 'high', 'low', 'close']]
    HA_df = df.copy()
    
    HA_df['close'] = round(
        ((new_df['open'] + new_df['high'] + new_df['low'] + new_df['close'])/4), 2)

    for i in range(len(new_df)):
        if i == 0:
            HA_df.iat[0, 0] = round(
                ((new_df['open'].iloc[0] + new_df['close'].iloc[0])/2), 2)
        else:
            HA_df.iat[i, 0] = round(
                ((HA_df.iat[i-1, 0] + HA_df.iat[i-1, 3])/2), 2)

    HA_df['high'] = HA_df.loc[:, ['open', 'close']].join(
        new_df['high']).max(axis=1)
    HA_df['low'] = HA_df.loc[:, ['open', 'close']].join(
        new_df['low']).min(axis=1)
    
    return HA_df

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, date, time, timedelta
import pytz

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

from keys import *

apikey = paper_apikey
secretkey = paper_secretkey

interval_dict = {
    '1Min': TimeFrame.Minute,
    '5Min': TimeFrame(5, TimeFrameUnit.Minute),
    '15Min': TimeFrame(15, TimeFrameUnit.Minute),
    '30Min': TimeFrame(30, TimeFrameUnit.Minute),
    '1Hr': TimeFrame.Hour,
    '4Hr': TimeFrame(4, TimeFrameUnit.Hour),
    '1Day': TimeFrame.Day,
    '1Week': TimeFrame.Week
}

duration_dict = {
    '1Day': timedelta(days=1),
    '1Week': timedelta(days=7),
    '1Month': timedelta(days=30),
    '3Months': timedelta(days=90),
    '1Year' : timedelta(days=365)
}


def stock_bars_from(ticker: str, timeframe: TimeFrame, start: datetime):
    stock_client = StockHistoricalDataClient(apikey, secretkey)
    # start = start.astimezone(pytz.timezone('US/Eastern')).astimezone(pytz.utc)
    request_params = StockBarsRequest(
        symbol_or_symbols=[ticker],
        timeframe=timeframe,
        start=start
    )
    bars = stock_client.get_stock_bars(request_params)
    if len(bars.data) == 0:
        return None
    else:
        df = bars.df
        return df.loc[ticker]


def determine_start_timeframe(timeframestr: str, timeperiodstr: str):
    timeframe = interval_dict[timeframestr]
    period_days = duration_dict[timeperiodstr]
    start = datetime.utcnow() - period_days
    return (start, timeframe)


def get_bars_dataframe(ticker, timeframestr: str, time_periodstr: str):
    start, timeframe = determine_start_timeframe(time_periodstr, timeframestr)
    df = stock_bars_from(ticker, timeframe=timeframe, start=start)
    return df


def get_current_price(ticker) -> float:
    client = StockHistoricalDataClient(apikey, secretkey)
    request_params = StockLatestQuoteRequest(symbol_or_symbols=ticker)
    latest_quote = client.get_stock_latest_quote(request_params)
    latest_ask_price = latest_quote[ticker].ask_price
    latest_bid_price = latest_quote[ticker].bid_price
    avg_price = (latest_ask_price + latest_bid_price) * 0.5
    return avg_price

# import pandas as pd
# def read_bars(fn: str):
#     df = pd.read_csv(f'/Users/ljp2/Alpaca/Data/bars1/{fn}.csv')
#     df['timestamp'] = pd.to_datetime(df.time)
#     df.drop('time',axis=1, inplace=True)
#     df.set_index('timestamp', drop=True, inplace=True)
#     return df
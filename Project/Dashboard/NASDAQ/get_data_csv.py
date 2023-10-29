from nasdaq import nasdaq
from others import others
import yfinance as yf
import pandas as pd


def get_stock_data(ticker_list, start_date, end_date):
    l = []

    for ticker in ticker_list:
        df = yf.download(ticker, start=start_date, end=end_date)
        df['Symbol'] = ticker
        df['Date'] = df.index
        df = df.reset_index(drop=True)
        l.append(df)

    # Concatenate all the dataframes vertically
    big_df =  pd.concat(l, axis=0)
    big_df = big_df.reset_index(drop=True)
    big_df.to_csv("stock_data.csv")

get_stock_data(nasdaq[:20], "2008-01-01", "2016-01-01")
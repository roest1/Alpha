import pandas as pd
import numpy as np

"""
bollinger_bands_signal_generation()

"""
def bollinger_bands_signal_generation(df, window=20, num_of_std=2):
    df['bollinger bands std'] = df['Close'].rolling(window=window, min_periods=20).std()
    df['bollinger bands mid band'] = df['Close'].rolling(
        window=window, min_periods=20).mean()
    df['bollinger bands upper band'] = df['bollinger bands mid band']+num_of_std*df['bollinger bands std']
    df['bollinger bands lower band'] = df['bollinger bands mid band']-num_of_std*df['bollinger bands std']

    df['bollinger bands signals'] = 0  # Default value is 0 for no signal
    df.loc[df['Close'] < df['bollinger bands lower band'],
           'bollinger bands signals'] = 1  # Buy signal
    df.loc[df['Close'] > df['bollinger bands upper band'],
           'bollinger bands signals'] = -1  # Sell signal

    del df['bollinger bands std']

    df = df.dropna()
    return df

"""
dual_thrust_signal_generation()


trigger_range should be smaller than one
normally ppl use 0.5 to give long and short 50/50 chance to trigger
"""
def dual_thrust_signal_generation(df, window=5, trigger_range=0.5):
    df['dual thrust range'] = np.maximum(
        df['High'].rolling(window=window).max() -
        df['Close'].rolling(window=window).min(),
        df['Close'].rolling(window=window).max() -
        df['Low'].rolling(window=window).min()
    )

    high_signal = trigger_range * \
        df['dual thrust range'].shift(window) + df['Close'].shift(window)
    low_signal = -(1 - trigger_range) * \
        df['dual thrust range'].shift(window) + df['Close'].shift(window)

    df['dual thrust signals'] = 0
    df.loc[df['Close'] > high_signal, 'dual thrust signals'] = 1
    df.loc[df['Close'] < low_signal, 'dual thrust signals'] = -1

    df['dual thrust upperbound'] = high_signal
    df['dual thrust lowerbound'] = low_signal

    del df['dual thrust range']
    df = df.dropna()

    return df

"""
heikin-ashi signal generation

# stop_loss: 
#stop loss positions, the maximum long positions we can get
#without certain constraints, you will long indefinites times 
#as long as the market condition triggers the signal
#in a whipsaw condition, it is suicidal
"""


def heikin_ashi_signal_generation(df, stop_loss=3):
    # heikin ashi close
    df['HA close'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4

    # initialize heikin ashi open
    df['HA open'] = pd.Series(0, index=df.index)
    df['HA open'].iloc[0] = df['Open'].iloc[0]

    # Calculate 'HA open' for the rest of the dataframe
    for n in range(1, len(df)):
        df['HA open'].iloc[n] = (
            df['HA open'].iloc[n-1] + df['HA close'].iloc[n-1]) / 2

    # heikin ashi high/low
    df['HA high'] = df[['HA open', 'HA close', 'High']].max(axis=1)
    df['HA low'] = df[['HA open', 'HA close', 'Low']].min(axis=1)

    df['HA signals'] = 0
    df['cumsum'] = 0

    for n in range(1, len(df)):
        if (df['HA open'].iloc[n] > df['HA close'].iloc[n] and
            df['HA open'].iloc[n] == df['HA high'].iloc[n] and
            np.abs(df['HA open'].iloc[n] - df['HA close'].iloc[n]) >
            np.abs(df['HA open'].iloc[n-1] - df['HA close'].iloc[n-1]) and
                df['HA open'].iloc[n-1] > df['HA close'].iloc[n-1]):

            df['HA signals'].iloc[n] = 1 if df['cumsum'].iloc[n-1] < stop_loss else 0

        elif (df['HA open'].iloc[n] < df['HA close'].iloc[n] and
              df['HA open'].iloc[n] == df['HA low'].iloc[n] and
              df['HA open'].iloc[n-1] < df['HA close'].iloc[n-1]):

            df['HA signals'].iloc[n] = -1 if df['cumsum'].iloc[n-1] > 0 else 0

        df['cumsum'].iloc[n] = df['HA signals'].iloc[:n+1].sum()

    del df['cumsum']
    df.dropna(inplace=True)
    return df

"""
awesome_signal_generation()


"""
def awesome_signal_generation(df, ma1=5, ma2=34):
    # Calculate moving averages
    df['awesome ma1'] = ((df['High'] + df['Low']) /
                         2).rolling(window=ma1).mean()
    df['awesome ma2'] = ((df['High'] + df['Low']) /
                         2).rolling(window=ma2).mean()

    # Initialize columns
    df['awesome signals'] = 0
    df['awesome oscillator'] = df['awesome ma1'] - df['awesome ma2']

    # Create conditions for saucer signals
    bearish_saucer = (
        (df['Open'] > df['Close']) &
        (df['Open'].shift(1) < df['Close'].shift(1)) &
        (df['Open'].shift(2) < df['Close'].shift(2)) &
        (df['awesome oscillator'].shift(1) > df['awesome oscillator'].shift(2)) &
        (df['awesome oscillator'].shift(1) < 0) &
        (df['awesome oscillator'] < 0)
    )

    bullish_saucer = (
        (df['Open'] < df['Close']) &
        (df['Open'].shift(1) > df['Close'].shift(1)) &
        (df['Open'].shift(2) > df['Close'].shift(2)) &
        (df['awesome oscillator'].shift(1) < df['awesome oscillator'].shift(2)) &
        (df['awesome oscillator'].shift(1) > 0) &
        (df['awesome oscillator'] > 0)
    )

    # Apply saucer signals
    df.loc[bearish_saucer, 'awesome signals'] = 1
    df.loc[bullish_saucer, 'awesome signals'] = -1

    # Create condition for moving average signals
    ma_signals = np.where(df['awesome ma1'] > df['awesome ma2'], 1,
                          np.where(df['awesome ma1'] < df['awesome ma2'], -1, 0))

    # Apply moving average signals, respecting the saucer signal priority
    df['awesome signals'] = np.where(
        (ma_signals == 1) & (df['awesome signals'] == 0), 1,
        np.where(
            (ma_signals == -1) & (df['awesome signals'] == 0), -1,
            df['awesome signals']
        )
    )

    # Apply the rule to ignore MA signals if there are previous positions
    df['cumsum'] = df['awesome signals'].cumsum()
    df['awesome signals'] = np.where(
        ((df['awesome signals'] == 1) & (df['cumsum'] > 1)) |
        ((df['awesome signals'] == -1) & (df['cumsum'] < 0)),
        0,
        df['awesome signals']
    )

    # Cleanup and return
    df.drop(['cumsum', 'awesome oscillator'], axis=1, inplace=True)
    df.dropna(inplace=True)
    return df


"""
macd_signal_generation()

"""
def macd_signal_generation(df, ma1=5, ma2=34):

    df['macd ma1'] = df['Close'].ewm(span=ma1).mean()
    df['macd ma2'] = df['Close'].ewm(span=ma2).mean()
    df['macd positions'] = 0
    df['macd positions'][ma1:] = np.where(
        df['macd ma1'][ma1:] >= df['macd ma2'][ma1:], 1, 0)
    df['macd signals'] = df['macd positions'].diff()
    #df['macd oscillator'] = df['macd ma1']-df['macd ma2']
    del df['macd positions']
    df = df.dropna()
    return df

"""
parabolic_sar_signal_generation()


"""
def parabolic_sar_signal_generation(df):
    initial_af = 0.02
    step_af = 0.02
    end_af = 0.2

    # Initializing columns
    df['trend'] = 0
    df['sar'] = 0.0
    df['real sar'] = 0.0
    df['ep'] = 0.0
    df['af'] = initial_af

    # Pre-calculating column indices
    trend_idx = df.columns.get_loc('trend')
    sar_idx = df.columns.get_loc('sar')
    real_sar_idx = df.columns.get_loc('real sar')
    ep_idx = df.columns.get_loc('ep')
    af_idx = df.columns.get_loc('af')
    high_idx = df.columns.get_loc('High')
    low_idx = df.columns.get_loc('Low')
    close_idx = df.columns.get_loc('Close')

    # Initial trend determination
    df.iloc[1, trend_idx] = 1 if df.iloc[1,
                                         close_idx] > df.iloc[0, close_idx] else -1

    # Initializing SAR, real SAR, and EP
    df.iloc[1, sar_idx] = df.iloc[0, high_idx] if df.iloc[1,
                                                          trend_idx] > 0 else df.iloc[0, low_idx]
    df.iloc[1, real_sar_idx] = df.iloc[1, sar_idx]
    df.iloc[1, ep_idx] = df.iloc[1, high_idx] if df.iloc[1,
                                                         trend_idx] > 0 else df.iloc[1, low_idx]

    # Loop over the DataFrame rows
    for i in range(2, len(df)):
        temp_sar = df.iloc[i-1, sar_idx] + df.iloc[i-1, af_idx] * \
            (df.iloc[i-1, ep_idx] - df.iloc[i-1, sar_idx])

        if df.iloc[i-1, trend_idx] < 0:
            sar = max(temp_sar, df.iloc[i-1, high_idx], df.iloc[i-2, high_idx])
            trend = 1 if sar < df.iloc[i,
                                       high_idx] else df.iloc[i-1, trend_idx] - 1
        else:
            sar = min(temp_sar, df.iloc[i-1, low_idx], df.iloc[i-2, low_idx])
            trend = -1 if sar > df.iloc[i,
                                        low_idx] else df.iloc[i-1, trend_idx] + 1

        # Assigning calculated values
        df.iloc[i, sar_idx] = sar
        df.iloc[i, trend_idx] = trend

        ep = (min(df.iloc[i, low_idx], df.iloc[i-1, ep_idx])
              if trend < 0 else max(df.iloc[i, high_idx], df.iloc[i-1, ep_idx]))
        df.iloc[i, ep_idx] = ep

        af = (initial_af if np.abs(trend) == 1 else
              min(end_af, df.iloc[i-1, af_idx] + step_af) if ep != df.iloc[i-1, ep_idx] else
              df.iloc[i-1, af_idx])
        df.iloc[i, af_idx] = af
        df.iloc[i, real_sar_idx] = ep if np.abs(trend) == 1 else sar

    df['positions'] = np.where(df['real sar'] < df['Close'], 1, 0)
    df['sar signals'] = df['positions'].diff()
    df = df.drop(columns=['trend', 'sar', 'ep', 'af', 'positions'])
    df = df.dropna()
    return df

"""
rsi_signal_generation()

"""
def rsi_signal_generation(df, lag_days=14):
    """
    smma()

    Smoothed moving average
    """
    def smma(series, n):

        output = [series[0]]

        for i in range(1, len(series)):
            temp = output[-1]*(n-1)+series[i]
            output.append(temp/n)

        return output
    """
    rsi()

    Several ways to calculate RSI
    - Simple moving avg
    - Exponentially weighted moving avg
    - etc

    Here we use smoothed moving avg
    """
    def rsi(data, n=14):

        delta = data.diff().dropna()

        up = np.where(delta > 0, delta, 0)
        down = np.where(delta < 0, -delta, 0)

        rs = np.divide(smma(up, n), smma(down, n))

        output = 100-100/(1+rs)

        return output[n-1:]

    df['rsi'] = 0.0
    df['rsi'][lag_days:] = rsi(df['Close'], n=lag_days)

    df['positions'] = np.select([df['rsi'] < 30, df['rsi'] > 70],
                                [1, -1], default=0)
    df['rsi signals'] = df['positions'].diff()
    df = df.drop(columns=['rsi', 'positions'])
    df = df.dropna()

    return df[lag_days:]

def get_all_indicators(data):
    df = data.copy()
    
    df = bollinger_bands_signal_generation(df)
    df = dual_thrust_signal_generation(df)
    df = heikin_ashi_signal_generation(df)
    df = awesome_signal_generation(df)
    df = macd_signal_generation(df)
    df = parabolic_sar_signal_generation(df)
    df = rsi_signal_generation(df)

    return df
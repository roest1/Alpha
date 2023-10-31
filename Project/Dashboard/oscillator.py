import numpy as np
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

"""
ewma_macd()

MACD with EWMA function to apply exponential smoothing
"""
def ewmacd(df, ma1, ma2):
    signals = df
    signals['macd ma1'] = signals['Close'].ewm(span=ma1).mean()    
    signals['macd ma2'] = signals['Close'].ewm(span=ma2).mean()   
    
    return signals

def signal_generation(df,method,ma1,ma2):
    
    signals=method(df,ma1,ma2)
    signals['macd positions']=0
    signals['macd positions'][ma1:]=np.where(signals['macd ma1'][ma1:]>=signals['macd ma2'][ma1:],1,0)
    signals['macd signals']=signals['macd positions'].diff()
    signals['macd oscillator']=signals['macd ma1']-signals['macd ma2']
    
    return signals
"""
awesome_ma()

Awesome oscillator 
Moving average is based on mean(high, low) instead of close price
"""
def awesome_ma(signals):
    
    signals['awesome ma1'],signals['awesome ma2']=0,0
    signals['awesome ma1']=((signals['High']+signals['Low'])/2).rolling(window=5).mean()
    signals['awesome ma2']=((signals['High']+signals['Low'])/2).rolling(window=34).mean()
    
    return signals

def awesome_signal_generation(df,method):
    
    signals=method(df).copy()
    if 'level_0' in signals.columns:
        signals.rename(columns={'level_0': 'old_index'}, inplace=True)
    signals.reset_index(inplace=True)
    signals['awesome signals']=0
    signals['awesome oscillator']=signals['awesome ma1']-signals['awesome ma2']  
    signals['cumsum']=0


    for i in range(2,len(signals)):

        #awesome oscillator has an extra way to generate signals
        #its called saucer
        #A Bearish Saucer setup occurs when the AO is below the Zero Line
        #in another word, awesome oscillator is negative
        #A Bearish Saucer entails two consecutive green bars (with the second bar being higher than the first bar) being followed by a red bar.
        #in another word, green bar refers to open price is higher than close price
    
        if (signals['Open'][i]>signals['Close'][i] and 
        signals['Open'][i-1]<signals['Close'][i-1] and 
        signals['Open'][i-2]<signals['Close'][i-2] and
        signals['awesome oscillator'][i-1]>signals['awesome oscillator'][i-2] and
        signals['awesome oscillator'][i-1]<0 and 
        signals['awesome oscillator'][i]<0):
            signals.at[i,'awesome signals']=1


        #this is bullish saucer
        #vice versa
        
        if (signals['Open'][i]<signals['Close'][i] and 
        signals['Open'][i-1]>signals['Close'][i-1] and 
        signals['Open'][i-2]>signals['Close'][i-2] and
        signals['awesome oscillator'][i-1]<signals['awesome oscillator'][i-2] and
        signals['awesome oscillator'][i-1]>0 and
        signals['awesome oscillator'][i]>0):
            signals.at[i,'awesome signals']=-1


        #this part is the same as macd signal generation
        #nevertheless, we have extra rules to get signals ahead of moving average
        #if we get signals before moving average generate any signal
        #we will ignore signals generated by moving average then
        #as it is delayed and probably deliver fewer profit than previous signals
        #we use cumulated sum to see if there has been created any open positions
        #if so, we will take a pass
        
        if signals['awesome ma1'][i]>signals['awesome ma2'][i]:
            signals.at[i,'awesome signals']=1
            signals['cumsum']=signals['awesome signals'].cumsum()
            if signals['cumsum'][i]>1:
                signals.at[i,'awesome signals']=0
            
        if signals['awesome ma1'][i]<signals['awesome ma2'][i]:
            signals.at[i,'awesome signals']=-1
            signals['cumsum']=signals['awesome signals'].cumsum()
            if signals['cumsum'][i]<0:
                signals.at[i,'awesome signals']=0
    
    signals['cumsum']=signals['awesome signals'].cumsum()
    
    return signals

@capture("graph")
def plot_awesome_positions_signals(data_frame: pd.DataFrame):
    df = awesome_signal_generation(data_frame, awesome_ma)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
    
    fig.add_trace(go.Scatter(x=df[df['awesome signals'] == 1]['Date'], 
                             y=df['awesome ma1'][df['awesome signals'] == 1], 
                             mode='markers', 
                             marker=dict(color='green', size=10, symbol='triangle-up'), 
                             name='Buy Signal'))

    fig.add_trace(go.Scatter(x=df[df['awesome signals'] == -1]['Date'], 
                             y=df['awesome ma1'][df['awesome signals'] == -1], 
                             mode='markers', 
                             marker=dict(color='red', size=10, symbol='triangle-down'), 
                             name='Sell Signal'))

    fig.update_layout(title='AWESOME Oscillator Buy/Sell Signals')

    return fig



@capture("graph")
def plot_macd_positions_signals(data_frame: pd.DataFrame):
    df = signal_generation(data_frame, ewmacd, 5, 34)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
    
    fig.add_trace(go.Scatter(x=df[df['macd signals'] == 1]['Date'], 
                             y=df['macd ma1'][df['macd signals'] == 1], 
                             mode='markers', 
                             marker=dict(color='green', size=10, symbol='triangle-up'), 
                             name='Buy Signal'))

    fig.add_trace(go.Scatter(x=df[df['macd signals'] == -1]['Date'], 
                             y=df['macd ma1'][df['macd signals'] == -1], 
                             mode='markers', 
                             marker=dict(color='red', size=10, symbol='triangle-down'), 
                             name='Sell Signal'))

    fig.update_layout(title='MACD Oscillator Buy/Sell Signals')

    return fig

@capture("graph")
def plot_awesome_oscillator_bar(data_frame: pd.DataFrame):
    df = awesome_signal_generation(data_frame, awesome_ma)

    fig = go.Figure()

    colors = np.where(df['Open'] > df['Close'], 'red', 'green')
    fig.add_trace(go.Bar(x=df['Date'], y=df['awesome oscillator'], marker_color=colors, name='Awesome Oscillator'))

    fig.update_layout(title='AWESOME Oscillator Bar')

    return fig

@capture("graph")
def plot_macd_oscillator_bar(data_frame: pd.DataFrame):
    df = signal_generation(data_frame, ewmacd, 5, 34)

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df['Date'], y=df['macd oscillator'], name='MACD Oscillator'))

    fig.update_layout(title='MACD Oscillator Bar')

    return fig

@capture("graph")
def plot_awesome_ma(data_frame: pd.DataFrame):
    df = awesome_signal_generation(data_frame, awesome_ma)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Date'], y=df['awesome ma1'], mode='lines', name='Awesome MA1'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['awesome ma2'], mode='lines', name='Awesome MA2', line=dict(dash='dot')))

    fig.update_layout(title='AWESOME Moving Average')

    return fig


@capture("graph")
def plot_macd_ma(data_frame: pd.DataFrame):
    df = signal_generation(data_frame, ewmacd, 5, 34)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Date'], y=df['macd ma1'], mode='lines', name='MACD MA1'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['macd ma2'], mode='lines', name='MACD MA2', line=dict(dash='dot')))

    fig.update_layout(title='MACD Moving Average')

    return fig


"""
portfolio()

capital0 : initial capital
positions : how many shares to buy for every single trade

"""
def portfolio(signals):
        
    capital0=5000
    positions=100

    portfolio=pd.DataFrame()
    portfolio['Close']=signals['Close']
    
    #cumsum is used to calculate the change of value while holding shares
    portfolio['awesome holding']=signals['cumsum']*portfolio['Close']*positions
    portfolio['macd holding']=signals['macd positions']*portfolio['Close']*positions

    #basically cash is initial capital minus the profit we make from every trade
    #note that we have to use cumulated sum to add every profit into our cash
    portfolio['awesome cash']=capital0-(signals['awesome signals']*portfolio['Close']*positions).cumsum()
    portfolio['macd cash']=capital0-(signals['macd signals']*portfolio['Close']*positions).cumsum()

    portfolio['awesome asset']=portfolio['awesome holding']+portfolio['awesome cash']
    portfolio['macd asset']=portfolio['macd holding']+portfolio['macd cash']

    portfolio['awesome return']=portfolio['awesome asset'].pct_change()
    portfolio['macd return']=portfolio['macd asset'].pct_change()
    
    return portfolio


@capture("graph")
def plot_macd_vs_awesome_profit(data_frame: pd.DataFrame):
    #awesome oscillator uses 5 lags as short ma
    #34 lags as long ma
    #for the consistent comparison
    #i apply the same to macd oscillator
    ma1=5
    ma2=34
    signals=signal_generation(data_frame, ewmacd, ma1, ma2)
    sigs = awesome_signal_generation(data_frame, awesome_ma)
    p = portfolio(sigs)
    fig = go.Figure()

    # Plotting Awesome Asset
    fig.add_trace(go.Scatter(x=p.index, y=p['awesome asset'], mode='lines', name='Awesome Asset'))

    # Plotting MACD Asset
    fig.add_trace(go.Scatter(x=p.index, y=p['macd asset'], mode='lines', name='MACD Asset'))

    fig.update_layout(title='Awesome VS MACD')

    return fig


"""
mdd()

Maximum drawdown

For every day, we take current asset value to compare with previous highest asset value
"""
def mdd(series):

    temp=0
    for i in range(1,len(series)):
        if temp>(series[i]/max(series[:i])-1):
            temp=(series[i]/max(series[:i])-1)

    return temp

def macd_vs_awesome_stats(df: pd.DataFrame) -> pd.DataFrame:
    #awesome oscillator uses 5 lags as short ma
    #34 lags as long ma
    #for the consistent comparison
    #i apply the same to macd oscillator
    ma1=5
    ma2=34
    signals = signal_generation(df, ewmacd, ma1, ma2)
    sigs=awesome_signal_generation(signals,awesome_ma)
    p = portfolio(sigs)
    stats=pd.DataFrame([0])

    #lets calculate some sharpe ratios
    #note that i set risk free return at 0 for simplicity
    #alternatively we can use snp500 as a benchmark
    stats['awesome sharpe']=(p['awesome asset'].iloc[-1]/5000-1)/np.std(p['awesome return'])
    stats['macd sharpe']=(p['macd asset'].iloc[-1]/5000-1)/np.std(p['macd return'])

    stats['awesome mdd']=mdd(p['awesome asset'])
    stats['macd mdd']=mdd(p['macd asset'])

    #print(stats)
    return stats

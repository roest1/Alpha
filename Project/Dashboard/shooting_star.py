import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vizro.models.types import capture


"""
shooting_star()

shooting star criteria
"""
def shooting_star(data,lower_bound,body_size):

    df=data.copy()

    #open>close,red color
    df['condition1']=np.where(df['Open']>=df['Close'],1,0)

    #a candle with little or no lower wick
    df['condition2']=np.where(
        (df['Close']-df['Low'])<lower_bound*abs(
            df['Close']-df['Open']),1,0)

    #a candle with a small lower body
    df['condition3']=np.where(abs(
        df['Open']-df['Close'])<abs(
        np.mean(df['Open']-df['Close']))*body_size,1,0)

    #a long upper wick that is at least two times the size of the lower body
    df['condition4']=np.where(
        (df['High']-df['Open'])>=2*(
            df['Open']-df['Close']),1,0)

    #price uptrend
    df['condition5']=np.where(
        df['Close']>=df['Close'].shift(1),1,0)
    df['condition6']=np.where(
        df['Close'].shift(1)>=df['Close'].shift(2),1,0)

    #the next candle's high must stay 
    #below the high of the shooting star 
    df['condition7']=np.where(
        df['High'].shift(-1)<=df['High'],1,0)

    #the next candle's close below 
    #the close of the shooting star
    df['condition8']=np.where(
        df['Close'].shift(-1)<=df['Close'],1,0)
    
    return df

"""
signal_generation()

8 criteria
"""
def signal_generation(df,method,
                      lower_bound=0.2,body_size=0.5,
                      stop_threshold=0.05,
                      holding_period=7):

    #get shooting star conditions
    data=method(df,lower_bound,body_size)

    #shooting star should suffice all conditions
    #in practise,you may find the definition too rigid
    #its important to relax a bit on the body size
    data['signals']=data['condition1']*data[
        'condition2']*data['condition3']*data[
        'condition4']*data['condition5']*data[
        'condition6']*data['condition7']*data[
        'condition8']

    #shooting star is a short signal
    data['signals']=-data['signals']
    
    #find exit position
    idxlist=data[data['signals']==-1].index
    for ind in idxlist:

        #entry point
        entry_pos=data['Close'].loc[ind]

        stop=False
        counter=0
        while not stop:
            ind+=1
            counter+=1

            #set stop loss/profit at +-5%
            if abs(data['Close'].loc[
                ind]/entry_pos-1)>stop_threshold:
                stop=True
                data['signals'].loc[ind]=1

            #set maximum holding period at 7 workdays
            if counter>=holding_period:
                stop=True
                data['signals'].loc[ind]=1

    #create positions
    data['positions']=data['signals'].cumsum()
    
    return data




@capture("graph")
def plot_shooting_star_candlesticks(data_frame: pd.DataFrame):
    # Preprocessing the dataframe
    data_frame.reset_index(inplace=True)
    data_frame['Date'] = pd.to_datetime(data_frame['Date'])
    
    # Signal generation
    new_data = signal_generation(data_frame, shooting_star)
    
    # Get subset for better viz to highlight shooting star
    subset = new_data.loc[5268:5283].copy()
    subset.reset_index(inplace=True, drop=True)
    
    fig = go.Figure(data=[go.Candlestick(x=subset['Date'],
                                         open=subset['Open'],
                                         high=subset['High'],
                                         low=subset['Low'],
                                         close=subset['Close'],
                                         increasing_line_color='red', 
                                         decreasing_line_color='green')])
    fig.update_layout(title=data_frame['Symbol'].iloc[0], xaxis_title='Date', yaxis_title='Price')
    
    return fig

@capture("graph")
def plot_shooting_star_positions(data_frame: pd.DataFrame):
    # Preprocessing the dataframe
    data_frame.reset_index(inplace=True)
    data_frame['Date'] = pd.to_datetime(data_frame['Date'])
    
    # Signal generation
    new_data = signal_generation(data_frame, shooting_star)
    
    # Get subset for better viz to highlight shooting star
    subset = new_data.loc[5268:5283].copy()
    subset.reset_index(inplace=True, drop=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=subset['Date'], y=subset['Close'], mode='lines', name='Close Price'))
    
    # Adding long/short positions
    fig.add_trace(go.Scatter(x=subset.loc[subset['signals']==-1]['Date'], 
                             y=subset['Close'].loc[subset['signals']==-1], 
                             mode='markers', marker_symbol='triangle-down', 
                             marker_color='red', name='Short'))
    fig.add_trace(go.Scatter(x=subset.loc[subset['signals']==1]['Date'], 
                             y=subset['Close'].loc[subset['signals']==1], 
                             mode='markers', marker_symbol='triangle-up', 
                             marker_color='green', name='Long'))
    
    fig.update_layout(title=data_frame['Symbol'].iloc[0], xaxis_title='Date', yaxis_title='Price')
    
    return fig


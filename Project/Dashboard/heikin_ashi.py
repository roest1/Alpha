import pandas as pd
import numpy as np
import scipy.integrate
import scipy.stats
import plotly.graph_objects as go
from vizro.models.types import capture

"""
portfolio()

capital0 : initial capital 
positions : how many shares to by in every position
"""
def portfolio(data,capital0=10000,positions=100):   
        
    #cumsum column is created to check the holding of the position
    data['cumsum']=data['signals'].cumsum()

    portfolio=pd.DataFrame()
    portfolio['holdings']=data['cumsum']*data['Close']*positions
    portfolio['cash']=capital0-(data['signals']*data['Close']*positions).cumsum()
    portfolio['total asset']=portfolio['holdings']+portfolio['cash']
    portfolio['return']=portfolio['total asset'].pct_change()
    portfolio['signals']=data['signals']
    portfolio['date']=data['Date']
    portfolio.set_index('date',inplace=True)

    return portfolio


"""
omega()

variation of sharpe ratio

Risk free return is replaced by a given threshold

Integration is used to calculate the return above and below threshold
- Could use summation for approximation

More reasonable ratio to measure risk adjusted return
- Normal distribution doesn't explain fat tail of returns
- student T cdf is used instead

Empirical distribution could be used, but is more complex
https://en.wikipedia.org/wiki/Omega_ratio
"""
def omega(risk_free,degree_of_freedom,maximum,minimum):

    y=scipy.integrate.quad(lambda g:1-scipy.stats.t.cdf(g,degree_of_freedom),risk_free,maximum)
    x=scipy.integrate.quad(lambda g:scipy.stats.t.cdf(g,degree_of_freedom),minimum,risk_free)

    z=(y[0])/(x[0])

    return z

"""
sortino()

Measures the impact of negative return on return

Another variation of sharpe ratio

std(all returns) substitued by std(negative returns)

Using student T probability distribution function instead of normal distribution
https://en.wikipedia.org/wiki/Sortino_ratio
"""
def sortino(risk_free,degree_of_freedom,growth_rate,minimum):

    v=np.sqrt(np.abs(scipy.integrate.quad(lambda g:((risk_free-g)**2)*scipy.stats.t.pdf(g,degree_of_freedom),risk_free,minimum)))
    s=(growth_rate-risk_free)/v[0]

    return s

"""
mdd()

Maximum drawdown

"""
def mdd(series):

    minimum=0
    for i in range(1,len(series)):
        if minimum>(series[i]/max(series[:i])-1):
            minimum=(series[i]/max(series[:i])-1)

    return minimum

"""
heikin_ashi()

Unique method to filter out noise
"""
def heikin_ashi(data):
    df=data.copy()
    
    df.reset_index(drop=True, inplace=True)

        
    #heikin ashi close
    df['HA close']=(df['Open']+df['Close']+df['High']+df['Low'])/4

    #initialize heikin ashi open
    df['HA open']=float(0)
    df['HA open'][0]=df['Open'][0]

    #heikin ashi open
    for n in range(1,len(df)):
        df.at[n,'HA open']=(df['HA open'][n-1]+df['HA close'][n-1])/2
        
    #heikin ashi high/low
    temp=pd.concat([df['HA open'],df['HA close'],df['Low'],df['High']],axis=1)
    df['HA high']=temp.apply(max,axis=1)
    df['HA low']=temp.apply(min,axis=1)

    del df['Adj Close']
    del df['Volume']
    
    return df

"""
signal_generation()

trigger condition of short strategy is the reverse of the long strategy

"""
def signal_generation(df,method,stls):
        
    data=method(df)
    
    data['signals']=0

    #i use cumulated sum to check how many positions i have longed
    #i would ignore the exit signal prior if not holding positions
    #i also keep tracking how many long positions i have got
    #long signals cannot exceed the stop loss limit
    data['cumsum']=0

    for n in range(1,len(data)):
        
        #long triggered
        if (data['HA open'][n]>data['HA close'][n] and data['HA open'][n]==data['HA high'][n] and
            np.abs(data['HA open'][n]-data['HA close'][n])>np.abs(data['HA open'][n-1]-data['HA close'][n-1]) and
            data['HA open'][n-1]>data['HA close'][n-1]):
            
            data.at[n,'signals']=1
            data['cumsum']=data['signals'].cumsum()


            #accumulate too many longs
            if data['cumsum'][n]>stls:
                data.at[n,'signals']=0
        
        #exit positions
        elif (data['HA open'][n]<data['HA close'][n] and data['HA open'][n]==data['HA low'][n] and 
        data['HA open'][n-1]<data['HA close'][n-1]):
            
            data.at[n,'signals']=-1
            data['cumsum']=data['signals'].cumsum()
        

            #clear all longs
            #if there are no long positions in my portfolio
            #ignore the exit signal
            if data['cumsum'][n]>0:
                data.at[n,'signals']=-1*(data['cumsum'][n-1])

            if data['cumsum'][n]<0:
                data.at[n,'signals']=0
                
    return data

# def stats(portfolio,trading_signals,stdate,eddate,capital0=10000):

#     stats=pd.DataFrame([0])

#     #get the min and max of return
#     maximum=np.max(portfolio['return'])
#     minimum=np.min(portfolio['return'])    

#     #growth_rate denotes the average growth rate of portfolio 
#     #use geometric average instead of arithmetic average for percentage growth
#     growth_rate=(float(portfolio['total asset'].iloc[-1]/capital0))**(1/len(trading_signals))-1

#     #calculating the standard deviation
#     std=float(np.sqrt((((portfolio['return']-growth_rate)**2).sum())/len(trading_signals)))

#     #use S&P500 as benchmark
#     benchmark=yf.download('^GSPC',start=stdate,end=eddate)

#     #return of benchmark
#     return_of_benchmark=float(benchmark['Close'].iloc[-1]/benchmark['Open'].iloc[0]-1)

#     #rate_of_benchmark denotes the average growth rate of benchmark 
#     #use geometric average instead of arithmetic average for percentage growth
#     rate_of_benchmark=(return_of_benchmark+1)**(1/len(trading_signals))-1

#     del benchmark

#     #backtesting stats
#     #CAGR stands for cumulated average growth rate
#     stats['CAGR']=stats['portfolio return']=float(0)
#     stats['CAGR'][0]=growth_rate
#     stats['portfolio return'][0]=portfolio['total asset'].iloc[-1]/capital0-1
#     stats['benchmark return']=return_of_benchmark
#     stats['sharpe ratio']=(growth_rate-rate_of_benchmark)/std
#     stats['maximum drawdown']=mdd(portfolio['total asset'])

#     #calmar ratio is sorta like sharpe ratio
#     #the standard deviation is replaced by maximum drawdown
#     #it is the measurement of return after worse scenario adjustment
#     #check wikipedia for more details
#     # https://en.wikipedia.org/wiki/Calmar_ratio
#     stats['calmar ratio']=growth_rate/stats['maximum drawdown']
#     stats['omega ratio']=omega(rate_of_benchmark,len(trading_signals),maximum,minimum)
#     stats['sortino ratio']=sortino(rate_of_benchmark,len(trading_signals),growth_rate,minimum)

#     #note that i use stop loss limit to limit the numbers of longs
#     #and when clearing positions, we clear all the positions at once
#     #so every long is always one, and short cannot be larger than the stop loss limit
#     stats['numbers of longs']=trading_signals['signals'].loc[trading_signals['signals']==1].count()
#     stats['numbers of shorts']=trading_signals['signals'].loc[trading_signals['signals']<0].count()
#     stats['numbers of trades']=stats['numbers of shorts']+stats['numbers of longs']  

#     #to get the total length of trades
#     #given that cumsum indicates the holding of positions
#     #we can get all the possible outcomes when cumsum doesnt equal zero
#     #then we count how many non-zero positions there are
#     #we get the estimation of total length of trades
#     stats['total length of trades']=trading_signals['signals'].loc[trading_signals['cumsum']!=0].count()
#     stats['average length of trades']=stats['total length of trades']/stats['numbers of trades']
#     stats['profit per trade']=float(0)
#     stats['profit per trade'].iloc[0]=(portfolio['total asset'].iloc[-1]-capital0)/stats['numbers of trades'].iloc[0]

#     del stats[0]
    #print(stats) # return stats to DataFrameDisplayer


# def candlestick(df, highcol='High', lowcol='Low', opencol='Open', closecol='Close', xcol='Date', colorup='red', colordown='green'):
#     # Create a candlestick chart using plotly.graph_objects
#     fig = go.Figure(data=[go.Candlestick(x=df[xcol],
#                                          open=df[opencol],
#                                          high=df[highcol],
#                                          low=df[lowcol],
#                                          close=df[closecol],
#                                          increasing_line_color=colorup,
#                                          decreasing_line_color=colordown)])
#    return fig

@capture("graph")
def plot_heikin_ashi_candlesticks(data_frame: pd.DataFrame):    
    
    #stop loss positions, the maximum long positions we can get
    #without certain constraints, you will long indefinites times 
    #as long as the market condition triggers the signal
    #in a whipsaw condition, it is suicidal
    stls=3
    df = signal_generation(data_frame, heikin_ashi, stls)
    # Create a subplot figure with two rows and a single column
    fig = go.Figure()

    # First subplot: Heikin-Ashi candlestick
    fig.add_trace(go.Candlestick(x=df['Date'],
                                 open=df['HA open'],
                                 high=df['HA high'],
                                 low=df['HA low'],
                                 close=df['HA close'],
                                 increasing_line_color='red',
                                 decreasing_line_color='green',
                                 name='Heikin-Ashi'))

    # Second subplot: Actual price with long/short positions
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name=df['Symbol'].iloc[0]))
    
    # Adding long positions (green triangle-up markers)
    long_positions = df[df['signals'] == 1]
    fig.add_trace(go.Scatter(x=long_positions['Date'], y=long_positions['Close'], mode='markers', marker_symbol='triangle-up', marker_color='green', name='Long'))
    
    # Adding short positions (red triangle-down markers)
    short_positions = df[df['signals'] < 0]
    fig.add_trace(go.Scatter(x=short_positions['Date'], y=short_positions['Close'], mode='markers', marker_symbol='triangle-down', marker_color='red', name='Short'))

    # Update layout to have two subplots with shared x-axis
    fig.update_layout(title='Heikin-Ashi with Actual Prices',
                      xaxis=dict(domain=[0, 0.9]),
                      yaxis=dict(title='HA price'),
                      yaxis2=dict(title='Price', anchor='x', overlaying='y', side='right'),
                      template="plotly_white")

    return fig

@capture("graph")
def plot_heikin_ashi_profit(data_frame: pd.DataFrame):


    #stop loss positions, the maximum long positions we can get
    #without certain constraints, you will long indefinites times 
    #as long as the market condition triggers the signal
    #in a whipsaw condition, it is suicidal
    stls=3
    signals = signal_generation(data_frame, heikin_ashi, stls)
    p = portfolio(signals)
    # Create a new figure
    fig = go.Figure()

    # Plotting the total asset value
    fig.add_trace(go.Scatter(x=p.index, y=p['total asset'], mode='lines', name='Total Asset'))

    # Adding long positions (green triangle-up markers)
    long_positions = p[p['signals'] == 1]
    fig.add_trace(go.Scatter(x=long_positions.index, y=long_positions['total asset'], mode='markers', marker_symbol='triangle-up', marker_color='green', name='Long'))
    
    # Adding short positions (red triangle-down markers)
    short_positions = p[p['signals'] < 0]
    fig.add_trace(go.Scatter(x=short_positions.index, y=short_positions['total asset'], mode='markers', marker_symbol='triangle-down', marker_color='red', name='Short'))

    # Update layout specifications
    fig.update_layout(title='Total Asset',
                      xaxis_title='Date',
                      yaxis_title='Asset Value',
                      template="plotly_white")
    
    return fig

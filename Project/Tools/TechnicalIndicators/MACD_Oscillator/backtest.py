import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

"""
macd()

Simple moving average
"""
def macd(signals, ma1, ma2):
    
    
    signals['ma1']=signals['Close'].rolling(window=ma1,min_periods=1,center=False).mean()
    signals['ma2']=signals['Close'].rolling(window=ma2,min_periods=1,center=False).mean()
    
    return signals

"""
signal_generation()

Short(MA) > Long(MA) ⟹ Long hold
Short(MA) < Long(MA) ⟹ clear positions
"""
def signal_generation(df,method, ma1, ma2):
    
    signals=method(df, ma1, ma2)
    signals['positions']=0

    #positions becomes and stays one once the short moving average is above long moving average
    signals['positions'][ma1:]=np.where(signals['ma1'][ma1:]>=signals['ma2'][ma1:],1,0)

    #as positions only imply the holding
    #we take the difference to generate real trade signal
    signals['signals']=signals['positions'].diff()

    #oscillator is the difference between two moving average
    #when it is positive, we long, vice versa
    signals['oscillator']=signals['ma1']-signals['ma2']

    return signals

"""
plot()

for backtest
"""
def plot(new, ticker):
    
    #the first plot is the actual close price with long/short positions
    fig=plt.figure()
    ax=fig.add_subplot(111)
    
    new['Close'].plot(label=ticker)
    ax.plot(new.loc[new['signals']==1].index,new['Close'][new['signals']==1],label='LONG',lw=0,marker='^',c='g')
    ax.plot(new.loc[new['signals']==-1].index,new['Close'][new['signals']==-1],label='SHORT',lw=0,marker='v',c='r')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Positions')
    
    plt.show()
    
    #the second plot is long/short moving average with oscillator
    #note that i use bar chart for oscillator
    fig=plt.figure()
    cx=fig.add_subplot(211)

    new['oscillator'].plot(kind='bar',color='r')

    plt.legend(loc='best')
    plt.grid(True)
    plt.xticks([])
    plt.xlabel('')
    plt.title('MACD Oscillator')

    bx=fig.add_subplot(212)

    new['ma1'].plot(label='ma1')
    new['ma2'].plot(label='ma2',linestyle=':')
    
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

def main():
    
    #input the long moving average and short moving average period
    #for the classic MACD, it is 12 and 26
    #once a upon a time you got six trading days in a week
    #so it is two week moving average versus one month moving average
    #for now, the ideal choice would be 10 and 21
    
    #global ma1,ma2,stdate,eddate,ticker,slicer

    #macd is easy and effective
    #there is just one issue
    #entry signal is always late
    #watch out for downward EMA spirals!
  
    # in 2020, there was a significant fluctuation due to 
    # COVID 
    ma1 = 12
    ma2 = 26
    stdate = '2020-01-01'
    eddate = '2020-12-31'
    ticker = 'AAPL'
  
    # ma1=int(input('ma1:')) # short moving average : typically 12
    # ma2=int(input('ma2:')) # long moving average : typically 26
    # stdate=input('start date in format yyyy-mm-dd:')
    # eddate=input('end date in format yyyy-mm-dd:')
    # ticker=input('ticker:')

    #slicing the downloaded dataset
    #if the dataset is too large, backtesting plot would look messy
    #you get too many markers cluster together
    #slicer=int(input('slicing:')) # set to 0 to see performance for entire year
    slicer = 0
    #downloading data
    df=yf.download(ticker,start=stdate,end=eddate)
    
    new=signal_generation(df,macd, ma1, ma2)
    new=new[slicer:]
    plot(new, ticker)


    #calculate stats with code from Heikin-Ashi_Candlestick/backtest.py
    

if __name__ == '__main__':
    main()
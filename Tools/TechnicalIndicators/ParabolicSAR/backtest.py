import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

"""
parabolic_sar()

sar calculation
"""
def parabolic_sar(new):
    
    #this is common accelerating factors for forex and commodity
    #for equity, af for each step could be set to 0.01
    initial_af=0.02
    step_af=0.02
    end_af=0.2
    
    
    new['trend']=0
    new['sar']=0.0
    new['real sar']=0.0
    new['ep']=0.0
    new['af']=0.0

    #initial values for recursive calculation
    #new['trend'][1]=1 if new['Close'][1]>new['Close'][0] else -1
    new.at[1, 'trend'] = 1 if new.at[1, 'Close'] > new.at[0, 'Close'] else -1 # fix error

    
    new['sar'][1]=new['High'][0] if new['trend'][1]>0 else new['Low'][0]
    new.at[1,'real sar']=new['sar'][1]
    new['ep'][1]=new['High'][1] if new['trend'][1]>0 else new['Low'][1]
    new['af'][1]=initial_af

    #calculation
    for i in range(2,len(new)):
        
        temp=new['sar'][i-1]+new['af'][i-1]*(new['ep'][i-1]-new['sar'][i-1])
        if new['trend'][i-1]<0:
            new.at[i,'sar']=max(temp,new['High'][i-1],new['High'][i-2])
            temp=1 if new['sar'][i]<new['High'][i] else new['trend'][i-1]-1
        else:
            new.at[i,'sar']=min(temp,new['Low'][i-1],new['Low'][i-2])
            temp=-1 if new['sar'][i]>new['Low'][i] else new['trend'][i-1]+1
        new.at[i,'trend']=temp
    
        
        if new['trend'][i]<0:
            temp=min(new['Low'][i],new['ep'][i-1]) if new['trend'][i]!=-1 else new['Low'][i]
        else:
            temp=max(new['High'][i],new['ep'][i-1]) if new['trend'][i]!=1 else new['High'][i]
        new.at[i,'ep']=temp
    
    
        if np.abs(new['trend'][i])==1:
            temp=new['ep'][i-1]
            new.at[i,'af']=initial_af
        else:
            temp=new['sar'][i]
            if new['ep'][i]==new['ep'][i-1]:
                new.at[i,'af']=new['af'][i-1]
            else:
                new.at[i,'af']=min(end_af,new['af'][i-1]+step_af)
        new.at[i,'real sar']=temp
       
        
    return new

"""
signal_generation()

same idea as macd oscillator
"""
def signal_generation(df,method):
    
    new=method(df)

    new['positions'],new['signals']=0,0
    new['positions']=np.where(new['real sar']<new['Close'],1,0)
    new['signals']=new['positions'].diff()
    
    return new

"""
plot()

plot sar and trade positions (similar to macd)
"""
def plot(new,ticker):
    
    fig=plt.figure()
    ax=fig.add_subplot(111)
    
    new['Close'].plot(lw=3,label='%s'%ticker)
    new['real sar'].plot(linestyle=':',label='Parabolic SAR',color='k')
    ax.plot(new.loc[new['signals']==1].index,new['Close'][new['signals']==1],marker='^',color='g',label='LONG',lw=0,markersize=10)
    ax.plot(new.loc[new['signals']==-1].index,new['Close'][new['signals']==-1],marker='v',color='r',label='SHORT',lw=0,markersize=10)
    
    plt.legend()
    plt.grid(True)
    plt.title('Parabolic SAR')
    plt.ylabel('price')
    plt.show()

def main():
    
    #download data via fix yahoo finance library
    stdate=('2016-01-01')
    eddate=('2018-01-01')
    ticker=('EA')

    #slice is used for plotting
    #a two year dataset with 500 variables would be too much for a figure
    slicer=450

    df=yf.download(ticker,start=stdate,end=eddate)
    
    #delete adj close and volume
    #as we dont need them
    del df['Adj Close']
    del df['Volume']

    #no need to iterate over timestamp index
   # df.reset_index(inplace=True)
    df.reset_index(inplace=True, drop=False) # fix errors
    df.rename(columns={'Date': 'date'}, inplace=True)


    new=signal_generation(df,parabolic_sar)

    #convert back to time series for plotting
    #so that we get a date x axis
    new.set_index(new['date'],inplace=True)

    #shorten our plotting horizon and plot
    new=new[slicer:]
    plot(new,ticker) 

    # calculate stats with code from Heikin-Ashi_Candlestick/backtest.py


if __name__ == '__main__':
    main()

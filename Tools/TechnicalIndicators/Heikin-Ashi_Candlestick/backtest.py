import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import scipy.integrate
import scipy.stats

"""
heikin_ashi()

Unique method to filter out noise
"""
def heikin_ashi(df):
    df=data.copy()
    
    df.reset_index(inplace=True)
        
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

"""
candlestick()

to plot candlesticks
"""
def candlestick(df,ax=None,titlename='',highcol='High',lowcol='Low',
                opencol='Open',closecol='Close',xcol='Date',
                colorup='r',colordown='g',**kwargs):  
    
    #bar width
    #use 0.6 by default
    dif=[(-3+i)/10 for i in range(7)]
    
    if not ax:
        ax=plt.figure(figsize=(10,5)).add_subplot(111)
    
    #construct the bars one by one
    for i in range(len(df)):
        
        #width is 0.6 by default
        #so 7 data points required for each bar
        x=[i+j for j in dif]
        y1=[df[opencol].iloc[i]]*7
        y2=[df[closecol].iloc[i]]*7

        barcolor=colorup if y1[0]>y2[0] else colordown
        
        #no high line plot if open/close is high
        if df[highcol].iloc[i]!=max(df[opencol].iloc[i],df[closecol].iloc[i]):
            
            #use generic plot to viz high and low
            #use 1.001 as a scaling factor
            #to prevent high line from crossing into the bar
            plt.plot([i,i],
                     [df[highcol].iloc[i],
                      max(df[opencol].iloc[i],
                          df[closecol].iloc[i])*1.001],c='k',**kwargs)
    
        #same as high
        if df[lowcol].iloc[i]!=min(df[opencol].iloc[i],df[closecol].iloc[i]):             
            
            plt.plot([i,i],
                     [df[lowcol].iloc[i],
                      min(df[opencol].iloc[i],
                          df[closecol].iloc[i])*0.999],c='k',**kwargs)
        
        #treat the bar as fill between
        plt.fill_between(x,y1,y2,
                         edgecolor='k',
                         facecolor=barcolor,**kwargs)

    #only show 5 xticks
    plt.xticks(range(0,len(df),len(df)//5),df[xcol][0::len(df)//5].dt.date)
    plt.title(titlename)

"""
plot()

backtest result
"""
def plot(df,ticker):    
    
    df.set_index(df['Date'],inplace=True)
    
    #first plot is Heikin-Ashi candlestick
    #use candlestick function and set Heikin-Ashi O,C,H,L
    ax1=plt.subplot2grid((200,1), (0,0), rowspan=120,ylabel='HA price')
    candlestick(df,ax1,titlename='',highcol='HA high',lowcol='HA low',
                opencol='HA open',closecol='HA close',xcol='Date',
                colorup='r',colordown='g')
    plt.grid(True)
    plt.xticks([])
    plt.title('Heikin-Ashi')


    #the second plot is the actual price with long/short positions as up/down arrows
    ax2=plt.subplot2grid((200,1), (120,0), rowspan=80,ylabel='price',xlabel='')
    df['Close'].plot(ax=ax2,label=ticker)

    #long/short positions are attached to the real close price of the stock
    #set the line width to zero
    #thats why we only observe markers
    ax2.plot(df.loc[df['signals']==1].index,df['Close'][df['signals']==1],marker='^',lw=0,c='g',label='long')
    ax2.plot(df.loc[df['signals']<0].index,df['Close'][df['signals']<0],marker='v',lw=0,c='r',label='short')

    plt.grid(True)
    plt.legend(loc='best')
    plt.show()


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
profit()

asset value of portfolio
"""
def profit(portfolio):
        
    fig=plt.figure()
    bx=fig.add_subplot(111)
    
    portfolio['total asset'].plot(label='Total Asset')
    
    #long/short position markers related to the portfolio
    #the same mechanism as the previous one
    #replace close price with total asset value
    bx.plot(portfolio['signals'].loc[portfolio['signals']==1].index,portfolio['total asset'][portfolio['signals']==1],lw=0,marker='^',c='g',label='long')
    bx.plot(portfolio['signals'].loc[portfolio['signals']<0].index,portfolio['total asset'][portfolio['signals']<0],lw=0,marker='v',c='r',label='short')
    
    plt.legend(loc='best')
    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('Asset Value')
    plt.title('Total Asset')
    plt.show()

"""
omega()

variation of sharpe ratio

Risk free return is replaced by a given threshold


https://en.wikipedia.org/wiki/Omega_ratio
"""

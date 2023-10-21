"""
Need to acquire one minute frequency data

Can use this website:

* Uses New York time zone utc -5 for non summer daylight savings

* London market starts at GMT 8am = EST 3am

http://www.histdata.com/download-free-forex-data/?/excel/1-minute-bar-quotes

- We get one minute freq. bid-ask price

⟹ Average of these is used to obtain price
"""
import pandas as pd
import matplotlib.pyplot as plt

def london_breakout(df):
    
    df['signals']=0

    #cumsum is the cumulated sum of signals
    #later we would use it to control our positions
    df['cumsum']=0

    #upper and lower are our thresholds
    df['upper']=0.0
    df['lower']=0.0

    return df

def signal_generation(df,method):
    
    #tokyo_price is a list to store average price of
    #the last trading hour of tokyo market
    #we use max, min to define the real threshold later
    tokyo_price=[]

    #risky_stop is a parameter set by us
    #it is to reduce the risk exposure to volatility
    #i am using 100 basis points
    #for instance, we have defined our upper and lower thresholds
    #however, when london market opens
    #the price goes skyrocketing 
    #say 200 basis points above upper threshold
    #i personally wouldnt get in the market as its too risky
    #also, my stop loss and target is 50 basis points
    #just half of my risk interval
    #i will use this variable for later stop loss set up
    risky_stop=0.01

    #this is another parameter set by us
    #it is about how long opening volatility would wear off
    #for me, 30 minutes after the market opening is the boundary
    #as long as its under 30 minutes after the market opening
    #if the price reaches threshold level, i will trade on signals
    open_minutes=30

    #this is the price when we execute a trade
    #we need to save it to set up the stop loss
    executed_price=float(0)
    
    signals=method(df)
    signals['date']=pd.to_datetime(signals['date'])
    
    #this is the core part
    #the time complexity for this part is extremely high
    #as there are too many constraints
    #if u have a better idea to optimize it
    #plz let me know

    for i in range(len(signals)):
        
        #as mentioned before
        #the dataset use eastern standard time
        #so est 2am is the last hour before london starts
        #we try to append all the price into the list called threshold
        if signals['date'][i].hour==2:
            tokyo_price.append(signals['price'][i])
            
        #est 3am which is gmt 8am
        #thats when london market starts
        #good morning city of london and canary wharf!
        #right at this moment
        #we get max and min of the price of tokyo trading hour
        #we set up the threshold as the way it is
        #alternatively, we can put 10 basis points above and below thresholds
        #we also use upper and lower list to keep track of our thresholds
        #and now we clear the list called threshold
        elif signals['date'][i].hour==3 and signals['date'][i].minute==0:

            upper=max(tokyo_price)
            lower=min(tokyo_price)

            signals.at[i,'upper']=upper
            signals.at[i,'lower']=lower

            tokyo_price=[]
            
        #prior to 30 minutes i have mentioned before
        #as long as its under 30 minutes after market opening
        #signals will be generated once conditions are met
        #this is a relatively risky way
        #alternatively, we can set the signal generation time at a fixed point
        #when its gmt 8 30 am, we check the conditions to see if there is any signal
        elif signals['date'][i].hour==3 and signals['date'][i].minute<open_minutes:

            #again, we wanna keep track of thresholds during signal generation periods
            signals.at[i,'upper']=upper
            signals.at[i,'lower']=lower
            
            #this is the condition of signals generation
            #when the price is above upper threshold
            #we set signals to 1 which implies long
            if signals['price'][i]-upper>0:
                signals.at[i,'signals']=1

                #we use cumsum to check the cumulated sum of signals
                #we wanna make sure that
                #only the first price above upper threshold triggers the signal
                #also, if it goes skyrocketing
                #say 200 basis points above, which is 100 above our risk tolerance
                #we set it as a false alarm
                signals['cumsum']=signals['signals'].cumsum()

                if signals['price'][i]-upper>risky_stop:
                    signals.at[i,'signals']=0

                elif signals['cumsum'][i]>1:
                    signals.at[i,'signals']=0

                else:

                    #we also need to store the price when we execute a trade
                    #its for stop loss calculation
                    executed_price=signals['price'][i]

            #vice versa    
            if signals['price'][i]-lower<0:
                signals.at[i,'signals']=-1

                signals['cumsum']=signals['signals'].cumsum()

                if lower-signals['price'][i]>risky_stop:
                    signals.at[i,'signals']=0

                elif signals['cumsum'][i]<-1:
                    signals.at[i,'signals']=0

                else:
                    executed_price=signals['price'][i]
                    
        #when its gmt 5 pm, london market closes
        #we use cumsum to see if there is any position left open
        #we take -cumsum as a signal
        #if there is no open position, -0 is still 0
        elif signals['date'][i].hour==12:
            signals['cumsum']=signals['signals'].cumsum()
            signals.at[i,'signals']=-signals['cumsum'][i]
            
        #during london trading hour after opening but before closing
        #we still use cumsum to check our open positions
        #if there is any open position
        #we set our condition at original executed price +/- half of the risk interval
        #when it goes above or below our risk tolerance
        #we clear positions to claim profit or loss
        else:
            signals['cumsum']=signals['signals'].cumsum()
            
            if signals['cumsum'][i]!=0:
                if signals['price'][i]>executed_price+risky_stop/2:
                    signals.at[i,'signals']=-signals['cumsum'][i]
                    
                if signals['price'][i]<executed_price-risky_stop/2:
                    signals.at[i,'signals']=-signals['cumsum'][i]
    
    return signals

def plot(new, signals):
    
    #the first plot is price with LONG/SHORT positions
    fig=plt.figure()
    ax=fig.add_subplot(111)

    new['price'].plot(label='price')

    ax.plot(new.loc[new['signals']==1].index,new['price'][new['signals']==1],lw=0,marker='^',c='g',label='LONG')
    ax.plot(new.loc[new['signals']==-1].index,new['price'][new['signals']==-1],lw=0,marker='v',c='r',label='SHORT')
      
    #this is the part where i add some vertical line to indicate market beginning and ending
    date=new.index[0].strftime('%Y-%m-%d')
    #plt.axvline('%s 03:00:00'%(date),linestyle=':',c='k')
    #plt.axvline('%s 12:00:00'%(date),linestyle=':',c='k')
    plt.axvline(pd.Timestamp('%s 03:00:00' % date), linestyle=':', c='k')
    plt.axvline(pd.Timestamp('%s 12:00:00' % date), linestyle=':', c='k')


    plt.legend(loc='best')
    plt.title('London Breakout')
    plt.ylabel('price')
    plt.xlabel('Date')
    plt.grid(True)
    plt.show()


    #lets look at the market opening and break it down into 110 minutes
    #we wanna observe how the price goes beyond the threshold

    f='%s 02:50:00'%(date)
    l='%s 03:30:00'%(date)
    news=signals[f:l]
    fig=plt.figure()
    bx=fig.add_subplot(111)

    bx.plot(news.loc[news['signals']==1].index,news['price'][news['signals']==1],lw=0,marker='^',markersize=10,c='g',label='LONG')
    bx.plot(news.loc[news['signals']==-1].index,news['price'][news['signals']==-1],lw=0,marker='v',markersize=10,c='r',label='SHORT')

    #i only need to plot non zero thresholds
    #zero is the value outta market opening period 
    bx.plot(news.loc[news['upper']!=0].index,news['upper'][news['upper']!=0],lw=0,marker='.',markersize=7,c='#BC8F8F',label='upper threshold')
    bx.plot(news.loc[news['lower']!=0].index,news['lower'][news['lower']!=0],lw=0,marker='.',markersize=5,c='#FF4500',label='lower threshold')
    bx.plot(news['price'],label='price')


    plt.grid(True)
    plt.ylabel('price')
    plt.xlabel('time interval')
    plt.xticks([])
    plt.title('%s Market Opening'%date)
    plt.legend(loc='best')
    plt.show()


def main():
    
    df=pd.read_csv('gbpusd.csv')

    signals=signal_generation(df,london_breakout)

    new=signals
    new.set_index(pd.to_datetime(signals['date']),inplace=True)
    date=new.index[0].strftime('%Y-%m-%d')
    #new=new['%s'%date]
    new = new.loc[date] # fix error

    plot(new, signals)

    #how to calculate stats can be found in Heikin-Ashi_Candlestick/backtest.py

if __name__ == '__main__':
    main()

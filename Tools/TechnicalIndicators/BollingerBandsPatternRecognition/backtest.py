import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy


"""
bollinger_bands()

calculates the 3 bands
"""
def bollinger_bands(df, window=20, num_of_std=2):
    
    data = copy.deepcopy(df)
     
    data['std'] = data['price'].rolling(window=window, min_periods=20).std()
    data['mid band'] = data['price'].rolling(window=window, min_periods=20).mean()
    
    data['upper band']=data['mid band']+num_of_std*data['std']
    data['lower band']=data['mid band']-num_of_std*data['std']
    
    return data

"""
signal_generation()

"""
def signal_generation(data,method):
    
    #according to investopedia
    #for a double bottom pattern
    #we should use 3-month horizon which is 75
    period=75
    
    #alpha denotes the difference between price and bollinger bands
    #if alpha is too small, its unlikely to trigger a signal
    #if alpha is too large, its too easy to trigger a signal
    #which gives us a higher probability to lose money
    #beta denotes the scale of bandwidth
    #when bandwidth is larger than beta, it is expansion period
    #when bandwidth is smaller than beta, it is contraction period
    alpha=0.0001
    beta=0.0001
    
    df=method(data)
    df['signals']=0
    
    #as usual, cumsum denotes the holding position
    #coordinates store five nodes of w shape
    #later we would use these coordinates to draw a w shape
    df['cumsum']=0
    df['coordinates']=''
    
    for i in range(period,len(df)):
        
        #moveon is a process control
        #if moveon==true, we move on to verify the next condition
        #if false, we move on to the next iteration
        #threshold denotes the value of node k
        #we would use it for the comparison with node m
        #plz refer to condition 3
        moveon=False
        threshold=0.0
        
        #bottom w pattern recognition
        #there is another signal generation method called walking the bands
        #i personally think its too late for following the trend
        #after confirmation of several breakthroughs
        #maybe its good for stop and reverse
        #condition 4
        if (df['price'][i]>df['upper band'][i]) and \
        (df['cumsum'][i]==0):
            
            for j in range(i,i-period,-1):                
                
                #condition 2
                if (np.abs(df['mid band'][j]-df['price'][j])<alpha) and \
                (np.abs(df['mid band'][j]-df['upper band'][i])<alpha):
                    moveon=True
                    break
            
            if moveon==True:
                moveon=False
                for k in range(j,i-period,-1):
                    
                    #condition 1
                    if (np.abs(df['lower band'][k]-df['price'][k])<alpha):
                        threshold=df['price'][k]
                        moveon=True
                        break
                        
            if moveon==True:
                moveon=False
                for l in range(k,i-period,-1):
                    
                    #this one is for plotting w shape
                    if (df['mid band'][l]<df['price'][l]):
                        moveon=True
                        break
                    
            if moveon==True:
                moveon=False        
                for m in range(i,j,-1):
                    
                    #condition 3
                    if (df['price'][m]-df['lower band'][m]<alpha) and \
                    (df['price'][m]>df['lower band'][m]) and \
                    (df['price'][m]<threshold):
                        df.at[i,'signals']=1
                        df.at[i,'coordinates']='%s,%s,%s,%s,%s'%(l,k,j,m,i)
                        df['cumsum']=df['signals'].cumsum()
                        moveon=True
                        break
        
        #clear our positions when there is contraction on bollinger bands
        #contraction on the bandwidth is easy to understand
        #when price momentum exists, the price would move dramatically for either direction
        #which greatly increases the standard deviation
        #when the momentum vanishes, we clear our positions
        
        #note that we put moveon in the condition
        #just in case our signal generation time is contraction period
        #but we dont wanna clear positions right now
        if (df['cumsum'][i]!=0) and \
        (df['std'][i]<beta) and \
        (moveon==False):
            df.at[i,'signals']=-1
            df['cumsum']=df['signals'].cumsum()
            
    return df

def plot(new):
    
    #as usual we could cut the dataframe into a small slice
    #for a tight and neat figure
    #a and b denotes entry and exit of a trade
    a,b=list(new[new['signals']!=0].iloc[:2].index)
    
    newbie=new[a-85:b+30]
    newbie.set_index(pd.to_datetime(newbie['date'], format='%Y-%m-%d %H:%M'), inplace=True)

   
    fig=plt.figure(figsize=(10,5))
    ax=fig.add_subplot(111)
    
    #plotting positions on price series and bollinger bands
    ax.plot(newbie['price'],label='price')
    ax.fill_between(newbie.index,newbie['lower band'],newbie['upper band'],alpha=0.2,color='#45ADA8')
    ax.plot(newbie['mid band'],linestyle='--',label='moving average',c='#132226')
    ax.plot(newbie['price'][newbie['signals']==1],marker='^',markersize=12, \
            lw=0,c='g',label='LONG')
    ax.plot(newbie['price'][newbie['signals']==-1],marker='v',markersize=12, \
            lw=0,c='r',label='SHORT')
    
    #plotting w shape
    #we locate the coordinates then find the exact date as index
    temp=newbie['coordinates'][newbie['signals']==1]
    indexlist=list(map(int,temp[temp.index[0]].split(',')))
    ax.plot(newbie['price'][pd.to_datetime(new['date'].iloc[indexlist])], \
            lw=5,alpha=0.7,c='#FE4365',label='double bottom pattern')
    
    #add some captions
    plt.text((newbie.loc[newbie['signals']==1].index[0]), \
             newbie['lower band'][newbie['signals']==1],'Expansion',fontsize=15,color='#563838')
    plt.text((newbie.loc[newbie['signals']==-1].index[0]), \
             newbie['lower band'][newbie['signals']==-1],'Contraction',fontsize=15,color='#563838')
    
    plt.legend(loc='best')
    plt.title('Bollinger Bands Pattern Recognition')
    plt.ylabel('price')
    plt.grid(True)
    plt.show()

def main():
    
    # download data from histdata.com and
    # take the average of bid and ask price
    df=pd.read_csv('gbpusd.csv')
    
    signals=signal_generation(df,bollinger_bands)

    new=copy.deepcopy(signals)
    plot(new)

if __name__ == '__main__':
    main()
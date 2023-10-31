import copy
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vizro.models.types import capture

"""
bollinger_bands()

calculates the 3 bands
"""
def bollinger_bands(df, window=20, num_of_std=2):
    
    data = copy.deepcopy(df)
     
    data['std'] = data['Close'].rolling(window=window, min_periods=20).std()
    data['mid band'] = data['Close'].rolling(window=window, min_periods=20).mean()
    
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
        try:
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
            if (df['Close'][i]>df['upper band'][i]) and \
            (df['cumsum'][i]==0):
                
                for j in range(i,i-period,-1):                
                    
                    #condition 2
                    if (np.abs(df['mid band'][j]-df['Close'][j])<alpha) and \
                    (np.abs(df['mid band'][j]-df['upper band'][i])<alpha):
                        moveon=True
                        break
                
                if moveon==True:
                    moveon=False
                    for k in range(j,i-period,-1):
                        
                        #condition 1
                        if (np.abs(df['lower band'][k]-df['Close'][k])<alpha):
                            threshold=df['Close'][k]
                            moveon=True
                            break
                            
                if moveon==True:
                    moveon=False
                    for l in range(k,i-period,-1):
                        
                        #this one is for plotting w shape
                        if (df['mid band'][l]<df['Close'][l]):
                            moveon=True
                            break
                        
                if moveon==True:
                    moveon=False        
                    for m in range(i,j,-1):
                        
                        #condition 3
                        if (df['Close'][m]-df['lower band'][m]<alpha) and \
                        (df['Close'][m]>df['lower band'][m]) and \
                        (df['Close'][m]<threshold):
                            df.at[i,'signals']=1
                            df.at[i,'coordinates']='%s,%s,%s,%s,%s'%(l,k,j,m,i)
                            df['cumsum']=df['signals'].cumsum()
                            moveon=True
                            break
        except KeyError:
            continue
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


@capture("graph")
def plot_bollinger_bands(data_frame: pd.DataFrame):
    df_prices = data_frame[['Date', 'Close']]
    signals = signal_generation(df_prices, bollinger_bands)
    new = copy.deepcopy(signals)
    
    # Check the number of signals
    indices = list(new[new['signals'] != 0].index)
    
    if len(indices) >= 2:
        a, b = indices[:2]
        newbie = new[a-85:b+30]
    else:
        newbie = new
        
    newbie.set_index(pd.to_datetime(newbie['Date'], format='%Y-%m-%d'), inplace=True)

    
    # Create a new figure with plotly.graph_objects
    fig = go.Figure()
    
    # Add price series
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['Close'], mode='lines', name='price'))
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['upper band'], fill=None, mode='lines', line_color='#45ADA8', name='upper band'))
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['lower band'], fill='tonexty', mode='lines', fillcolor='rgba(69, 173, 168, 0.2)', line_color='#45ADA8', name='lower band'))
    
    # Add Moving Average
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['mid band'], mode='lines', line=dict(dash='dash', color='#132226'), name='moving average'))
    
    if len(indices) >= 2:
        # Mark LONG and SHORT positions
        fig.add_trace(go.Scatter(x=newbie[newbie['signals']==1].index, y=newbie['Close'][newbie['signals']==1], mode='markers', marker=dict(symbol='triangle-up', size=12, color='green'), name='LONG'))
        fig.add_trace(go.Scatter(x=newbie[newbie['signals']==-1].index, y=newbie['Close'][newbie['signals']==-1], mode='markers', marker=dict(symbol='triangle-down', size=12, color='red'), name='SHORT'))
        
        # Plotting w shape
        temp = newbie['coordinates'][newbie['signals'] == 1]
        indexlist = list(map(int, temp[temp.index[0]].split(',')))
        w_dates = pd.to_datetime(new['Date'].iloc[indexlist])
        fig.add_trace(go.Scatter(x=w_dates, y=newbie['Close'][w_dates], mode='lines', line=dict(width=3, color='#FE4365'), name='double bottom pattern'))
        
        # Add captions as annotations
        annotations = [
            dict(x=newbie.loc[newbie['signals']==1].index[0], y=newbie['lower band'][newbie['signals']==1], text='Expansion', showarrow=False, font=dict(size=15, color='#563838')),
            dict(x=newbie.loc[newbie['signals']==-1].index[0], y=newbie['lower band'][newbie['signals']==-1], text='Contraction', showarrow=False, font=dict(size=15, color='#563838'))
        ]
        fig.update_layout(annotations=annotations)
    
    # Title, labels, and other layout specifications
    fig.update_layout(title='Bollinger Bands Pattern Recognition', yaxis_title='Price', xaxis_title='Date', template="plotly_white")
    
    # Return the figure
    return fig
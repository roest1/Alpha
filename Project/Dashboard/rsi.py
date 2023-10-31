import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vizro.models.types import capture


"""
smma()

Smoothed moving average
"""
def smma(series,n):
    
    output=[series[0]]
    
    for i in range(1,len(series)):
        temp=output[-1]*(n-1)+series[i]
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
def rsi(data,n=14):
    
    delta=data.diff().dropna()
    
    up=np.where(delta>0,delta,0)
    down=np.where(delta<0,-delta,0)
    
    rs=np.divide(smma(up,n),smma(down,n))
    
    output=100-100/(1+rs)
    
    return output[n-1:]

"""
signal_generation()

RSI > 70 ⟹ short stock
RSI < 30 ⟹ long stock
"""
def signal_generation(df,method,n=14):
    
    df['rsi']=0.0
    df['rsi'][n:]=method(df['Close'],n=14)
    
    df['positions']=np.select([df['rsi']<30,df['rsi']>70], \
                              [1,-1],default=0)
    df['signals']=df['positions'].diff()
    
    return df[n:]

"""
pattern_recognition()

Unlike double bottom for bollinger bands
this head-shoulder pattern directly on rsi instead of price
"""
def pattern_recognition(df,method,lag=14):
    
    df['rsi']=0.0
    df['rsi'][lag:]=method(df['Close'],lag)    
    
    #as usual, period is defined as the horizon for finding the pattern
    period=25    
    
    #delta is the threshold of the difference between two prices
    #if the difference is smaller than delta
    #we can conclude two prices are not significantly different from each other
    #the significant level is defined as delta
    delta=0.2
    
    #these are the multipliers of delta
    #we wanna make sure there is head and shoulders are significantly larger than other nodes
    #the significant level is defined as head/shoulder multiplier*delta
    head=1.1
    shoulder=1.1
    
    df['signals']=0
    df['cumsum']=0
    df['coordinates']=''
    
    #now these are the parameters set by us based on experience
    #entry_rsi is the rsi when we enter a trade
    #we would exit the trade based on two conditions
    #one is that we hold the stock for more than five days
    #the variable for five days is called exit_days
    #we use a variable called counter to keep track of it
    #two is that rsi has increased more than 4 since the entry
    #the variable for 4 is called exit_rsi
    #when either condition is triggered, we exit the trade
    #this is a lazy way to exit the trade
    #cuz i dont wanna import indicators from other scripts
    #i would suggest people to use other indicators such as macd or bollinger bands
    #exiting trades based on rsi is definitely inefficient and unprofitable
    entry_rsi=0.0
    counter=0
    exit_rsi=4
    exit_days=5
    
    #signal generation
    #plz refer to the following link for pattern visualization
    # https://github.com/je-suis-tm/quant-trading/blob/master/preview/rsi%20head-shoulder%20pattern.png
    #the idea is to start with the first node i
    #we look backwards and find the head node j with maximum value in pattern finding period
    #between node i and node j, we find a node k with its value almost the same as node i
    #started from node j to left, we find a node l with its value almost the same as node i
    #between the left beginning and node l, we find a node m with its value almost the same as node i
    #after that, we find the shoulder node n with maximum value between node m and node l
    #finally, we find the shoulder node o with its value almost the same as node n
    for i in range(period+lag,len(df)):
        
        #this is pretty much the same idea as in bollinger bands
        #except we have two variables
        #one for shoulder and one for the bottom nodes
        moveon=False
        top=0.0
        bottom=0.0
        
        #we have to make sure no holding positions
        #and the close price is not the maximum point of pattern finding horizon
        if (df['cumsum'].iloc[i]==0) and  \
        (df['Close'].iloc[i]!=max(df['Close'].iloc[i-period:i])):
            
            #get the head node j with maximum value in pattern finding period
            #note that dataframe is in datetime index
            #we wanna convert the result of idxmax to a numerical index number
            j=df.index.get_loc(df['Close'][i-period:i].idxmax())
            
            #if the head node j is significantly larger than node i
            #we would move on to the next phrase
            if (np.abs(df['Close'].iloc[j]-df['Close'].iloc[i])>head*delta):
                bottom=df['Close'].iloc[i]
                moveon=True
            
            #we try to find node k between node j and node i
            #if node k is not significantly different from node i
            #we would move on to the next phrase
            if moveon==True:
                moveon=False
                for k in range(j,i):    
                    if (np.abs(df['Close'].iloc[k]-bottom)<delta):
                        moveon=True
                        break
            
            #we try to find node l between node j and the end of pattern finding horizon
            #note that we start from node j to the left
            #cuz we need to find another bottom node m later which would start from the left beginning
            #this way we can make sure we would find a shoulder node n between node m and node l
            #if node l is not significantly different from node i
            #we would move on to the next phrase
            if moveon==True:
                moveon=False
                for l in range(j,i-period+1,-1):
                    if (np.abs(df['Close'].iloc[l]-bottom)<delta):
                        moveon=True
                        break
                    
            #we try to find node m between node l and the end of pattern finding horizon
            #this time we start from left to right as usual
            #if node m is not significantly different from node i
            #we would move on to the next phrase
            if moveon==True:
                moveon=False        
                for m in range(i-period,l):
                    if (np.abs(df['Close'].iloc[m]-bottom)<delta):
                        moveon=True
                        break
            
            #get the shoulder node n with maximum value between node m and node l
            #note that dataframe is in datetime index
            #we wanna convert the result of idxmax to a numerical index number
            #if node n is significantly larger than node i and significantly smaller than node j
            #we would move on to the next phrase
            if moveon==True:
                moveon=False        
                n=df.index.get_loc(df['Close'][m:l].idxmax())
                if (df['Close'].iloc[n]-bottom>shoulder*delta) and \
                (df['Close'].iloc[j]-df['Close'].iloc[n]>shoulder*delta):
                    top=df['Close'].iloc[n]
                    moveon=True
                    
            #we try to find shoulder node o between node k and node i
            #if node o is not significantly different from node n
            #we would set up the signals and coordinates for visualization
            #we also need to refresh cumsum and entry_rsi for exiting the trade
            #note that moveon is still set as True
            #it would help the algo to ignore this round of iteration for exiting the trade
            if moveon==True:        
                for o in range(k,i):
                    if (np.abs(df['Close'].iloc[o]-top)<delta):
                        df.at[df.index[i],'signals']=-1
                        df.at[df.index[i],'coordinates']='%s,%s,%s,%s,%s,%s,%s'%(m,n,l,j,k,o,i)
                        df['cumsum']=df['signals'].cumsum()
                        entry_rsi=df['rsi'].iloc[i]
                        moveon=True
                        break
        
        #each time we have a holding position
        #counter would steadily increase
        #if either of the exit conditions is met
        #we exit the trade with long position
        #and we refresh counter, entry_rsi and cumsum
        #you may wonder why do we need cumsum?
        #well, this is for holding positions in case you wanna check on portfolio performance
        if entry_rsi!=0 and moveon==False:
            counter+=1
            if (df['rsi'].iloc[i]-entry_rsi>exit_rsi) or \
            (counter>exit_days):
                df.at[df.index[i],'signals']=1
                df['cumsum']=df['signals'].cumsum()
                counter=0
                entry_rsi=0
            
    return df

@capture("graph")
def plot_rsi_positions(data_frame: pd.DataFrame):
    new = signal_generation(data_frame, rsi)
    
    
    fig = go.Figure()

    # Plotting the Close prices
    fig.add_trace(go.Scatter(x=new.index, y=new['Close'], mode='lines', name=new["Symbol"].iloc[0]))

    # Plotting the LONG signals
    fig.add_trace(go.Scatter(x=new[new['signals'] == 1].index,
                             y=new['Close'][new['signals'] == 1],
                             mode='markers',
                             marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='LONG'))

    # Plotting the SHORT signals
    fig.add_trace(go.Scatter(x=new[new['signals'] == -1].index,
                             y=new['Close'][new['signals'] == -1],
                             mode='markers',
                             marker=dict(symbol='triangle-down', size=10, color='red'),
                             name='SHORT'))

    # Updating the layout to add titles, labels
    fig.update_layout(
        title='RSI Positions',
        xaxis_title='Date',
        yaxis_title='Price',
    )
    
    return fig

@capture("graph")
def plot_rsi_head_shoulders(data_frame: pd.DataFrame):
    new = signal_generation(data_frame, rsi)
    
    fig = go.Figure()

    # Plotting the RSI values
    fig.add_trace(go.Scatter(x=new.index, y=new['rsi'], mode='lines', name='Relative Strength Index', line=dict(color='#522e75')))
    
    # Adding the shaded region for overbought/oversold range
    fig.add_shape(
        type="rect",
        x0=new.index[0],
        x1=new.index[-1],
        y0=30,
        y1=70,
        fillcolor="#f22f08",
        opacity=0.5,
        layer="below",
        line_width=0,
    )
    
    # Adding overbought and oversold annotations
    fig.add_annotation(
        x=new.index[-45],
        y=75,
        text="overbought",
        showarrow=False,
        font=dict(color="#594346", size=12.5),
        yshift=10
    )

    fig.add_annotation(
        x=new.index[-45],
        y=25,
        text="oversold",
        showarrow=False,
        font=dict(color="#594346", size=12.5),
        yshift=-10
    )

    # Updating the layout to add titles, labels
    fig.update_layout(
        title='RSI',
        xaxis_title='Date',
        yaxis_title='Value',
        template="plotly_white",  # This is to mimic the background grid of matplotlib
        showlegend=True
    )
    
    return fig


@capture("graph")
def plot_rsi_pattern_positions(data_frame: pd.DataFrame):
    new = pattern_recognition(data_frame, rsi)
    
    # Get a small slice of dataframe for a clear view of head-shoulder pattern
    a, b = list(new[new['signals'] != 0].iloc[2:4].index)
    temp = list(map(int, new['coordinates'][a].split(',')))
    c = new.index.get_loc(b)
    newbie = new[temp[0] - 30 : c + 20]
    
    fig = go.Figure()

    # Plotting the Close prices
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['Close'], mode='lines', name=new["Symbol"].iloc[0]))

    # Plotting the LONG signals
    fig.add_trace(go.Scatter(x=newbie[newbie['signals'] == 1].index,
                             y=newbie['Close'][newbie['signals'] == 1],
                             mode='markers',
                             marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='LONG'))

    # Plotting the SHORT signals
    fig.add_trace(go.Scatter(x=newbie[newbie['signals'] == -1].index,
                             y=newbie['Close'][newbie['signals'] == -1],
                             mode='markers',
                             marker=dict(symbol='triangle-down', size=10, color='red'),
                             name='SHORT'))

    # Updating the layout to add titles, labels
    fig.update_layout(
        title='RSI Pattern Positions',
        xaxis_title='Date',
        yaxis_title='Price',
        template="plotly_white"  # This is to mimic the background grid of matplotlib
    )
    
    return fig
    

@capture("graph")
def plot_rsi_pattern_head_shoulder(data_frame: pd.DataFrame):
    new = pattern_recognition(data_frame, rsi)
    
    a, b = list(new[new['signals'] != 0].iloc[2:4].index)
    temp = list(map(int, new['coordinates'][a].split(',')))
    indexlist = list(map(lambda x: new.index[x], temp))
    
    c = new.index.get_loc(b)
    newbie = new[temp[0] - 30 : c + 20]
    
    fig = go.Figure()

    # Plotting the RSI values
    fig.add_trace(go.Scatter(x=newbie.index, y=newbie['rsi'], mode='lines', name='Relative Strength Index', line=dict(color='#f4ed71')))
    
    # Plotting the head-shoulder pattern on RSI
    fig.add_trace(go.Scatter(x=indexlist, y=newbie['rsi'][indexlist],
                             mode='lines+markers',
                             name='Head-Shoulder Pattern',
                             line=dict(color='#8d2f23', width=3),
                             marker=dict(symbol='circle', size=6, color='#8d2f23')))
    
    # Plotting the LONG signals
    fig.add_trace(go.Scatter(x=newbie[newbie['signals'] == 1].index,
                             y=newbie['rsi'][newbie['signals'] == 1],
                             mode='markers',
                             marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='LONG'))

    # Plotting the SHORT signals
    fig.add_trace(go.Scatter(x=newbie[newbie['signals'] == -1].index,
                             y=newbie['rsi'][newbie['signals'] == -1],
                             mode='markers',
                             marker=dict(symbol='triangle-down', size=10, color='red'),
                             name='SHORT'))

    # Adding the shaded region for overbought/oversold range
    fig.add_shape(
        type="rect",
        x0=newbie.index[0],
        x1=newbie.index[-1],
        y0=30,
        y1=70,
        fillcolor="#000d29",
        opacity=0.6,
        line_width=0,
    )

    # Annotations for head and shoulders
    for i, label in [(1, 'Shoulder'), (3, 'Head'), (5, 'Shoulder')]:
        fig.add_annotation(
            x=indexlist[i],
            y=newbie['rsi'][indexlist[i]] + 2,
            text=label,
            showarrow=False,
            font=dict(color="#e4ebf2", size=10)
        )

    # Updating the layout to add titles, labels
    fig.update_layout(
        title='RSI Head-Shoulder Pattern',
        xaxis_title='Date',
        yaxis_title='RSI Value',
        template="plotly_white"
    )
    
    return fig

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


"""
parabolic_sar()

sar calculation
"""
def parabolic_sar(df):
    new = df.copy()
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
    
    new=method(df.copy())

    new['positions'],new['signals']=0,0
    new['positions']=np.where(new['real sar']<new['Close'],1,0)
    new['signals']=new['positions'].diff()
    
    return new

"""
plot()

plot sar and trade positions (similar to macd)
"""
@capture("graph")
def plot_parabolic_sar(data_frame:pd.DataFrame):
    #slice is used for plotting
    #a two year dataset with 500 variables would be too much for a figure
    slicer=450

    df = data_frame.copy()
    #delete adj close and volume
    #as we dont need them
    del df['Adj Close']
    del df['Volume']

    df.reset_index(inplace=True, drop=False) # fix errors
    df=signal_generation(df,parabolic_sar)

    #convert back to time series for plotting
    #so that we get a date x axis
    df.set_index(df['Date'],inplace=True)

    #shorten our plotting horizon and plot
    df=df[slicer:]
    

    fig = go.Figure()
    # Plotting the Close prices
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name=f'{df["Symbol"].iloc[0]}'))

    # Plotting the Parabolic SAR
    fig.add_trace(go.Scatter(x=df.index, y=df['real sar'], mode='lines', name='Parabolic SAR', line=dict(dash='dot', color='black')))

    # Plotting the LONG signals
    fig.add_trace(go.Scatter(x=df.loc[df['signals'] == 1].index, y=df['Close'][df['signals'] == 1], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='LONG'))

    # Plotting the SHORT signals
    fig.add_trace(go.Scatter(x=df.loc[df['signals'] == -1].index, y=df['Close'][df['signals'] == -1], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='SHORT'))

    # Updating the layout to add titles, labels
    fig.update_layout(
        title='Parabolic SAR',
        xaxis_title='Date',
        yaxis_title='Price'
    )
    return fig
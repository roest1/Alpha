import numpy as np
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

def signal_generation(df, rg, param, column):
    
    
    df['range1'] = df['High'].rolling(rg).max() - df['Close'].rolling(rg).min()
    df['range2'] = df['Close'].rolling(rg).max() - df['Low'].rolling(rg).min()
    df['range'] = np.where(df['range1'] > df['range2'], df['range1'], df['range2'])

    df['signals'] = 0
    df['cumsum'] = 0
    df['upper'] = 0.0
    df['lower'] = 0.0
    sigup = float(0)
    siglo = float(0)
    
    for i in df.index:
        # Set up thresholds
        try:
            sigup = float(param * df.at[i, 'range'] + df.at[i, column])
            siglo = float(-(1-param) * df.at[i, 'range'] + df.at[i, column])
        except TypeError:
            print(f"Error at index {i}. df.at[i, 'range']={df.at[i, 'range']}, df.at[i, column]={df.at[i, column]}")
            continue

        # Check for signals
        if (sigup != 0 and df.at[i, column] > sigup):
            df.at[i, 'signals'] = 1
        if (siglo != 0 and df.at[i, column] < siglo):
            df.at[i, 'signals'] = -1

        df['cumsum'] = df['signals'].cumsum()        
        if (df.at[i, 'cumsum'] > 1 or df.at[i, 'cumsum'] < -1):
            df.at[i, 'signals'] = 0
        
        # Update the thresholds
        df.at[i, 'upper'] = sigup
        df.at[i, 'lower'] = siglo

    return df


@capture("graph")
def plot_dual_thrust(data_frame: pd.DataFrame):

    df_copy = data_frame.copy()
    df_copy.set_index(pd.to_datetime(df_copy["Date"]), inplace=True)
    
    rg = 5
    param = 0.5
    column = 'Close'
    
    signals = signal_generation(df_copy, rg, param, column)
    
    # Use the last N days of data for visualization. Let's say N=30 for a month of data.
    N = 30
    signew = signals[-N:]

    # Create a new figure with plotly.graph_objects
    fig = go.Figure()

    # Plot the main data
    fig.add_trace(go.Scatter(x=signew.index, y=signew[column], mode='lines', name=column))

    # Add filled region for upper and lower bounds
    upper_bound = signew['upper']
    lower_bound = signew['lower']
    fig.add_trace(go.Scatter(x=upper_bound.index, y=upper_bound, fill=None, mode='lines', line_color='#355c7d', name='Upper Bound'))
    fig.add_trace(go.Scatter(x=lower_bound.index, y=lower_bound, fill='tonexty', mode='lines', fillcolor='rgba(53, 92, 125, 0.2)', line_color='#355c7d', name='Lower Bound'))

    # Add markers for LONG and SHORT positions
    fig.add_trace(go.Scatter(x=signew.loc[signew['signals'] == 1].index, y=signew[column][signew['signals'] == 1], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='LONG'))
    fig.add_trace(go.Scatter(x=signew.loc[signew['signals'] == -1].index, y=signew[column][signew['signals'] == -1], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='SHORT'))

    # Title, labels, and other layout specifications
    fig.update_layout(title='Dual Thrust', yaxis_title=column, xaxis_title='Date', template="plotly_white")

    # Return the figure
    return fig

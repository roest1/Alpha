
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import random

global colorlist # generate gradient colors
colorlist = ['#fffb77',
 '#fffa77',
 '#fff977',
 '#fff876',
 '#fff776',
 '#fff676',
 '#fff576',
 '#fff475',
 '#fff375',
 '#fff275',
 '#fff175',
 '#fff075',
 '#ffef74',
 '#ffef74',
 '#ffee74',
 '#ffed74',
 '#ffec74',
 '#ffeb73',
 '#ffea73',
 '#ffe973',
 '#ffe873',
 '#ffe772',
 '#ffe672',
 '#ffe572',
 '#ffe472',
 '#ffe372',
 '#ffe271',
 '#ffe171',
 '#ffe071',
 '#ffdf71',
 '#ffde70',
 '#ffdd70',
 '#ffdc70',
 '#ffdb70',
 '#ffda70',
 '#ffd96f',
 '#ffd86f',
 '#ffd76f',
 '#ffd66f',
 '#ffd66f',
 '#ffd56e',
 '#ffd46e',
 '#ffd36e',
 '#ffd26e',
 '#ffd16d',
 '#ffd06d',
 '#ffcf6d',
 '#ffce6d',
 '#ffcd6d',
 '#ffcc6c',
 '#ffcb6c',
 '#ffca6c',
 '#ffc96c',
 '#ffc86b',
 '#ffc76b',
 '#ffc66b',
 '#ffc56b',
 '#ffc46b',
 '#ffc36a',
 '#ffc26a',
 '#ffc16a',
 '#ffc06a',
 '#ffbf69',
 '#ffbe69',
 '#ffbd69',
 '#ffbd69',
 '#ffbc69',
 '#ffbb68',
 '#ffba68',
 '#ffb968',
 '#ffb868',
 '#ffb768',
 '#ffb667',
 '#ffb567',
 '#ffb467',
 '#ffb367',
 '#ffb266',
 '#ffb166',
 '#ffb066',
 '#ffaf66',
 '#ffad65',
 '#ffac65',
 '#ffab65',
 '#ffa964',
 '#ffa864',
 '#ffa763',
 '#ffa663',
 '#ffa463',
 '#ffa362',
 '#ffa262',
 '#ffa062',
 '#ff9f61',
 '#ff9e61',
 '#ff9c61',
 '#ff9b60',
 '#ff9a60',
 '#ff9860',
 '#ff975f',
 '#ff965f',
 '#ff955e',
 '#ff935e',
 '#ff925e',
 '#ff915d',
 '#ff8f5d',
 '#ff8e5d',
 '#ff8d5c',
 '#ff8b5c',
 '#ff8a5c',
 '#ff895b',
 '#ff875b',
 '#ff865b',
 '#ff855a',
 '#ff845a',
 '#ff8259',
 '#ff8159',
 '#ff8059',
 '#ff7e58',
 '#ff7d58',
 '#ff7c58',
 '#ff7a57',
 '#ff7957',
 '#ff7857',
 '#ff7656',
 '#ff7556',
 '#ff7455',
 '#ff7355',
 '#ff7155',
 '#ff7054',
 '#ff6f54',
 '#ff6d54',
 '#ff6c53',
 '#ff6b53',
 '#ff6953',
 '#ff6852',
 '#ff6752',
 '#ff6552',
 '#ff6451',
 '#ff6351',
 '#ff6250',
 '#ff6050',
 '#ff5f50',
 '#ff5e4f',
 '#ff5c4f',
 '#ff5b4f',
 '#ff5a4e',
 '#ff584e',
 '#ff574e',
 '#ff564d',
 '#ff544d',
 '#ff534d',
 '#ff524c',
 '#ff514c',
 '#ff4f4b',
 '#ff4e4b',
 '#ff4d4b',
 '#ff4b4a',
 '#ff4a4a']


"""
monte_carlo()

test_size : % of data to be used for testing
num_simulations : # simulations to run (theoretically the more the better)
"""
def monte_carlo(data, test_size = 0.5, num_simulations=100, **kwargs):
    df, test = train_test_split(data, test_size=test_size, shuffle=False, **kwargs)
    forecast_horizon = len(test)

    # use adjusted close price to account for dividends and stock splits
    df = df['Adj Close']

    log_returns = np.log(1 + df.pct_change())
    drift = log_returns.mean() - (0.5 * log_returns.var())

    predicted = {}

    
    for i in range(num_simulations):
        predicted[i] = [df.iloc[0]]

        # Generate price predictions
        # consider both historical data and forecast horizon
        for _ in range(len(df) + forecast_horizon - 1):
            # Standard normal distribution to generate random number
            temp = predicted[i][-1]*np.exp(drift + log_returns.std() * random.gauss(0, 1))
            predicted[i].append(temp.item())
    
    # Determine which simulation is best fit using min(standard deviation)
    std = float('inf')
    choice = 0
    for i in range(num_simulations):
        temp = np.std(np.subtract(predicted[i][:len(df)], df.values))
        if temp < std:
            std = temp
            choice = i
        
    return forecast_horizon, predicted, choice

import plotly.graph_objects as go
from vizro.models.types import capture

@capture("graph")
def monte_carlo_simulation(data_frame:pd.DataFrame=None):
    
    forecast_horizon, predicted, choice = monte_carlo(data_frame)

    fig = go.Figure()

    # Plotting the Actual data
    fig.add_trace(go.Scatter(x=data_frame["Date"][:len(data_frame)-forecast_horizon], 
                             y=data_frame['Close'].iloc[:len(data_frame)-forecast_horizon], 
                             mode='lines', 
                             name='Actual', 
                             line=dict(color='#d75b66', width=3)))

    # Plotting the predicted lines
    for i in range(int(len(predicted))):
        if i != choice:
            fig.add_trace(go.Scatter(x=data_frame['Date'][:len(data_frame)-forecast_horizon], 
                                     y=predicted[i][:len(data_frame)-forecast_horizon], 
                                     mode='lines', 
                                     opacity=0.05,
                                     showlegend=False))

    # Plotting the 'Best Fitted' line
    fig.add_trace(go.Scatter(x=data_frame["Date"][:len(data_frame)-forecast_horizon], 
                             y=predicted[choice][:len(data_frame)-forecast_horizon], 
                             mode='lines', 
                             name='Best Fitted',
                             line=dict(color='#5398d9', width=3)))

    fig.update_layout(title=f'Monte Carlo Simulation\nTicker: {data_frame["Symbol"].iloc[0]}')
    return fig



@capture("graph")
def monte_carlo_forecast(data_frame:pd.DataFrame=None):
    
    forecast_horizon, predicted, choice = monte_carlo(data_frame)

    fig = go.Figure()

    # Plotting the Actual data until forecast point
    fig.add_trace(go.Scatter(x=data_frame["Date"][:len(data_frame)-forecast_horizon], 
                             y=data_frame['Close'].iloc[:len(data_frame)-forecast_horizon], 
                             mode='lines', 
                             name='Actual', 
                             line=dict(color='#d75b66', width=3)))

    # Plotting the forecasted lines
    for i in range(int(len(predicted))):
        if i != choice:
            fig.add_trace(go.Scatter(x=data_frame['Date'][len(data_frame)-forecast_horizon:], 
                                     y=predicted[i][len(data_frame)-forecast_horizon:], 
                                     mode='lines', 
                                     opacity=0.05,
                                     showlegend=False))

    # Plotting the 'Best Fitted' forecasted line
    fig.add_trace(go.Scatter(x=data_frame["Date"][len(data_frame)-forecast_horizon:], 
                             y=predicted[choice][len(data_frame)-forecast_horizon:], 
                             mode='lines', 
                             name='Best Fitted',
                             line=dict(color='#5398d9', width=3)))

    fig.update_layout(title=f'Monte Carlo Forecast\nTicker: {data_frame["Symbol"].iloc[0]}')
    return fig

@capture("graph")
def monte_carlo_test(data_frame:pd.DataFrame=None, start=100, end=1000, delta=100, **kwargs):
    table = pd.DataFrame()
    table['Simulations'] = np.arange(start, end + delta, delta)
    table.set_index('Simulations', inplace=True)
    table['Prediction'] = 0

    # test accuracy for each prediction
    for i in np.arange(start, end + 1, delta):

        forecast_horizon, predicted, choice = monte_carlo(data_frame, num_simulations=i, **kwargs)

        true = np.sign(data_frame['Adj Close'].iloc[len(data_frame)-forecast_horizon] - data_frame['Adj Close'].iloc[-1])

        best_fit = np.sign(predicted[choice][len(data_frame) - forecast_horizon] - predicted[choice][-1])
        table.at[i, 'Prediction'] = np.where(true == best_fit, 1, -1)

    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(y=table.index.astype(str),
               x=table['Prediction'],
               orientation='h',
               marker=dict(color=np.where(table['Prediction'] == 1, '#5398d9', '#d75b66')))
    ])
    fig.update_layout(title=f"Prediction accuracy doesn't depend on the numbers of simulation.\nTicker: {data_frame['Symbol'].iloc[0]}",
                      xaxis=dict(tickvals=[-1,1], ticktext=['Failure','Success']),
                      yaxis_title="Times of Simulation",
                      xaxis_title="Prediction Accuracy")

    return fig
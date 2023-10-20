import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import random
from sklearn.model_selection import train_test_split

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

"""
plot()

plots two figures:

1. Plots every simulation and highlights best fit with true price

2. Plots best fit with true price on training and testing horizon
"""
def plot(df, forecast_horizon, predicted, choice, ticker):

    # Plot every simulation and highligh best fit with true price
    ax=plt.figure(figsize=(10,5)).add_subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for i in range(int(len(predicted))):
        if i!=choice:
            ax.plot(df.index[:len(df)-forecast_horizon], \
                    predicted[i][:len(df)-forecast_horizon], \
                    alpha=0.05)
    ax.plot(df.index[:len(df)-forecast_horizon], \
            predicted[choice][:len(df)-forecast_horizon], \
            c='#5398d9',linewidth=5,label='Best Fitted')
    df['Close'].iloc[:len(df)-forecast_horizon].plot(c='#d75b66',linewidth=5,label='Actual')
    plt.title(f'Monte Carlo Simulation\nTicker: {ticker}')
    plt.legend(loc=0)
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.show()

    # Plot training and testing horizons 
    # Compare best fit with true prices
    ax=plt.figure(figsize=(10,5)).add_subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.plot(predicted[choice],label='Best Fitted',c='#edd170')
    plt.plot(df['Close'].tolist(),label='Actual',c='#02231c')
    plt.axvline(len(df)-forecast_horizon,linestyle=':',c='k')
    plt.text(len(df)-forecast_horizon-50, \
             max(max(df['Close']),max(predicted[choice])),'Training', \
             horizontalalignment='center', \
             verticalalignment='center')
    plt.text(len(df)-forecast_horizon+50, \
             max(max(df['Close']),max(predicted[choice])),'Testing', \
             horizontalalignment='center', \
             verticalalignment='center')
    plt.title(f'Training versus Testing\nTicker: {ticker}\n')
    plt.legend(loc=0)
    plt.ylabel('Price')
    plt.xlabel('T+Days')
    plt.show()

"""
test()

Tests if increase in simulations increases the prediction accuracy

start : min(num_simulations)
end : max(num_simulations)
delta : # steps to reach end from start 
"""
def test(df, ticker, start=100, end=1000, delta=100, **kwargs):
    table = pd.DataFrame()
    table['Simulations'] = np.arange(start, end + delta, delta)
    table.set_index('Simulations', inplace=True)
    table['Prediction'] = 0

    # test accuracy for each prediction
    for i in np.arange(start, end + 1, delta):

        forecast_horizon, predicted, choice = monte_carlo(df, num_simulations = i, **kwargs)

        true = np.sign(df['Adj Close'].iloc[len(df)-forecast_horizon] - df['Adj Close'].iloc[-1])

        best_fit = np.sign(predicted[choice][len(df) - forecast_horizon] - predicted[choice][-1])
        table.at[i, 'Prediction'] = np.where(true == best_fit, 1, -1)
    
    # Show accuracy across number of simulations
    ax=plt.figure(figsize=(10,5)).add_subplot(111)
    ax.spines['right'].set_position('center')
    ax.spines['top'].set_visible(False)

    plt.barh(np.arange(1,len(table)*2+1,2),table['Prediction'], \
             color=colorlist[0::int(len(colorlist)/len(table))])

    plt.xticks([-1,1],['Failure','Success'])
    plt.yticks(np.arange(1,len(table)*2+1,2),table.index)
    plt.xlabel('Prediction Accuracy')
    plt.ylabel('Times of Simulation')
    plt.title(f"Prediction accuracy doesn't depend on the numbers of simulation.\nTicker: {ticker}\n")
    plt.show()

def main():
    print("Monte Carlo Simulation")
    
    # GE plunged 57.9% in 2018 due to long history of M&A failures
    # Monte Carlo will not be able to predict this
    start_at = '2016-01-15'
    end_at = '2019-01-15'
    ticker = 'GE'

    # NVDA dropped 75.6% due to the financial crisis in 2008
    # start_at = '2006-01-15'
    # end_at = '2009-01-15'
    # ticker = 'NVDA'

    df = yf.download(ticker, start = start_at, end = end_at)
    df.index = pd.to_datetime(df.index)

    forecast_horizon, predicted, choice = monte_carlo(df)
    plot(df, forecast_horizon, predicted, choice, ticker)
    test(df, ticker)
    print("Done!")

if __name__ == '__main__':
    main()


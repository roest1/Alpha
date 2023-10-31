import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
        sigup = float(param * df.at[i, 'range'] + df.at[i, column])
        siglo = float(-(1-param) * df.at[i, 'range'] + df.at[i, column])

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

def plot(signals, column):
    
    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)    
    
    ax.plot(signals.index, signals[column], label=column)
    ax.fill_between(signals.index, signals['upper'], signals['lower'], alpha=0.2, color='#355c7d')
    ax.plot(signals[signals['signals'] == 1].index, signals[column][signals['signals'] == 1], 'g^', label='LONG')
    ax.plot(signals[signals['signals'] == -1].index, signals[column][signals['signals'] == -1], 'rv', label='SHORT')
    
    plt.legend(loc='best')
    plt.ylabel(column)
    plt.xlabel('Date')
    plt.title('Dual Thrust')
    plt.grid(True)
    plt.show()

def main():
    
    # Assuming the CSV file provides daily prices with columns: Date, Open, High, Low, Close
    df = pd.read_csv('daily_prices.csv')
    df.set_index(pd.to_datetime(df['Date']), inplace=True)

    rg = 5
    param = 0.5
    column = 'Close'
    
    signals = signal_generation(df, rg, param, column)
    plot(signals, column)

if __name__ == '__main__':
    main()

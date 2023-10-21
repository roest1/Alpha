# MACD Oscillator

* Moving Average Convergence/Divergence

* Momentum strategy that believes up/down momentum has more impact on short term moving average than long term

* Very commonly used

---

**Strategy**

* Compute long and short term moving average on close price of a given stock

* compare moving averages of different time horizons to generate signals
    - Short term moving average > long term moving average ⟹ Long the stock 
    - Short term moving average < long term moving average ⟹ Short the stock


# Awesome Oscillator (upgraded MACD)

* Momentum strategy focussed on moving average

* Instead of taking moving average on close price, it is derived from the mean of high and low prices

* similar to MACD oscillator, it takes both short and long term moving averages to construct.

* Various strategies to generate signals, such as traditional moving average divergence, twin peaks (W pattern), and saucer

* We will use saucer in this example

* Saucer has the power to beat the slow response of traditional divergence
    - Faster response doesn't guarantee a less risky or more profitable outcome

* We will use MACD oscillator as control group to test if the awesome oscillator outperforms it

[Awesome Oscillator](https://www.tradingview.com/support/solutions/43000501826-awesome-oscillator-ao/)

---

* In the code, exponential smoothing is used on MACD and simple moving average is used on the awesome oscillator

* Compare the short moving average with the long moving average. If the difference is positive, we long the asset. If the difference is negative, we short the asset.


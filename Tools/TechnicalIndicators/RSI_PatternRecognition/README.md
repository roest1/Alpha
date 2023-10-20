# Relative Strength Index Pattern Recognition (RSI)

* Reflexts current strength/weakness of the stock price momentum

* Use 14 days of smoothed average to separately calculate the intra daily uptrend and downtrend

* Denote uptrend moving average divided by downtrend moving average as relative strength

* Normalize relative strength by 100 which becomes an index called RSI

* Common belief:
    - RSI > 70 ⟹ Overbought
    - RSI < 30 ⟹ Oversold

* Could be divergence between RSI momentum and price momentum
    - Not covered in script!

* Effectiveness of any divergence strategy on RSI is debatable

**Pattern Recognition**

* Unlike Bollinger Bands, we can directly look at the patterns of RSI instead of price

* In Bollinger Bands we tested double bottom, so here we test head-shoulder

[TradingView](https://www.tradingview.com/wiki/Relative_Strength_Index_(RSI)
)

---

**Strategies**

* There are a couple of strategies to use RSI

* Simplest one is overbought/oversold (this example)

* Another one is divergence between price and RSI
    - Inventor believed bearish RSI divergence creates selling opportunity
    - His protege believed bearish divergence only occurs in a bullish trend
    - (Contradiction) Who is right? We don't know.

* Last one is called failure swing
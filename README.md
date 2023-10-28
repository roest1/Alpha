# Alpha Project

---

## To Do:

* Get Data (WRDS Cloud?)

* Create volatility X momentum matrix
    - Calculations for volatility and momentum

## Questions:

* What strategies/indicators correspond to (volatility X momentum) combination

* Ways to compute momentum and volatility

## Notes:

* Heikin-Ashi_Candlestick/backtest.py is the only py file with stats calculation (will be used later probably)

* Options level output : [WRDS](https://wrds-www.wharton.upenn.edu/pages/get-data/option-suite-wrds/us-option-level-output/)

* Install bloomberg api : 

```bash
% python -m pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi
```
  
---

## Jobs

### Riley's doing:

**Still working on :**

* Get data

* QuantamentalAnalysis/
    - PortfolioOptimization
    - WidsomOfCrowds

* TechnicalIndicators/
    - DualThrust

* Summarizing Documents

### Trevor's doing:


---

## Parameter Checklist

(Parameters to record)

**Price/Returns/Contract**

* What strategy tested

* Underlying -> What stock
    - Price (open and close vlaues of net cost to open and close strategy)
    - Expiration
    - Strike Price

* Days Open

* Open Interest -> On strategy open

**Volatility (Values on open and close)**

* IV (30 day)

* Historical Volatility

* IV Percentile or Rank

**Momentum (Values on open and close)**

* Indicator Signals
    - RSI (14 period)
    - ADX
    - On balance volume % change open to close

**Events (IF applicable)**

* Earnings

* M&A

* Industry events (Exogeneous)
  
**Macro (Values on open and close)**

* VIX
    - Equities short term Volume

* MOVE Index
    - Fixed income volatility

* Yield Curve (10Y - 2Y maturities)
    - Current 10Y - 2Y = -.3

---


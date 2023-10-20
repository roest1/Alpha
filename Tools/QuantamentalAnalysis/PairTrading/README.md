# Pair Trading (Mean Reversion)


* Rely on assumption that two cointegrated stocks don't drift too far apart from each other
    - Normally a stock and an ETF index
    - Or two stocks in the same industry
    - Or any pair that passes the EG test

* Use Engle-Granger two step analysis to find cointegrated pairs

* Once cointegrated stocks are found, we standardize the residual and set one sigma away (two tailed) as the threshold. Then we compute the current standardized residual of the selected stocks. 
    - When standardized residual exceeds the threshold, it generates a trading signal

* Simple Rule: Always long the cheap stock and short the expensive stock.


---

* It is easy to find stocks that are correlated or cointegrated, however, statistically, most relationships break eventually. 
    - Important to check status quo of cointegration relationship regularly

* There is no such thing as riskless statistical arbitrage
    - Always check cointegration status before trading execution

**Example**

* NVDA and AMD are two GPU companies which could've been considered cointegrated. After the bitcoin mining boom and machine learning hype, NVDA skyrocketted and AMD didn't change much. Thus, the cointegrated relationship broke.
# London Breakout

* Intra-daily opening range breakout strategy

* Information arbitrage across different markets in different time zones

* FX (decentralised) market runs 24/7
    - London & Tokyo are two of the largest FX markets

* Tokyo FX trading hours : GMT 0:00 a.m. - GMT 8:59 a.m.
  
* London FX trading (no summer daylight savings): opens at GMT 8:00 a.m. 
    - Crucial timeframe : GMT 7:00 a.m. - GMT 7:59 a.m.

* London's crucial timeframe incorporates teh info of all overnight activities of financial market

* Taking advantage of FX 24 hour trading on weekdays

* Tokyo -> London -> New York -> Sydney -> Tokyo -> ...


---

**Strategy**

* Establish upper and lower thresholds prior to the high and low of the crucial timeframe

* Spend first couple minutes of London FX market open to see if price breaches boundaries
    - Above threshold ⟹ Long currency pair
    - Below threshold ⟹ Short currency pair

* Set limit to prevent us from trading the case of abnormal opening volatility

* Normally, we clear positions based on target stop loss or stop profit
    - If we still have open positions at the end of the trading hour, we close them


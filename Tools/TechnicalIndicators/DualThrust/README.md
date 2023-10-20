# Dual Thrust

* Upper and lower thresholds based on previous days' open, close, high, and low

* When open exceeds thresholld, we take long/short based on previous upper/lower thresholds

* No stop loss on this strategy
    - We reverse our positions when the price goes from one threshold to the other
    - Need to clear all positions by the end of day

* Similar to London Breakout

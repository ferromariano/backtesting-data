from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

from backtesting_data.history import historySymbol

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


## binance_futures_cm
ETHUSD_PERP = historySymbol('binance_futures_cm', 'ETHUSD_PERP',  interval='1m', limit=100)

#ETHUSD_PERP.info()
print(ETHUSD_PERP.head())

bt = Backtest(ETHUSD_PERP, SmaCross, cash=10000, commission=.002)
stats = bt.run()
print(stats)
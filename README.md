# Backtesting data

Accesde a datos historicos rapidamente :D para usar en backtesting.py

## Installation

    $ pip install backtesting backtesting-data

## Usage

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA
from backtesting_data import historySymbol
import datetime


class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


BTCUSDT = historyCoin('binanceusdm', 'BTCUSDT', '5m', 200, end_time=datetime.datetime(2024, 10, 25, 20, 30))

bt = Backtest(BTCUSDT, SmaCross, commission=.002,
              exclusive_orders=True)
stats = bt.run()
bt.plot()
```
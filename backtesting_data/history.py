import pandas as pd
from backtesting_data.utils.ManagerDbKline import ManagerDbKline, ManagerDbKlineExchange

def historySymbol(exchange_name, symbol, interval='5m', limit=100, end_time=None, cache=True) -> pd.DataFrame:
    
    exchange:ManagerDbKlineExchange = ManagerDbKline.getExchange(exchange_name, cache)
    
    return exchange.getDatatoEnd(symbol, interval, limit, end_time)

import ccxt
from backtesting_data.utils.exchange_ccxt_data import exchange_ccxt_data

class binance_spot(exchange_ccxt_data):
    _col_name_index = 'Index'
    _cols_kline = {
        'Index': 0,
        'Open': 1,
        'High': 2,
        'Low': 3,
        'Close': 4,
        'Volume': 5,
    }
    
    limit_kline = 1000
    
    def __init__(self, cache_path=None, cache_type=None):
        super().__init__(cache_path=cache_path, cache_type=cache_type)
        self._cache_path_exchange = 'binance_spot'
        self.public_name:str=self._cache_path_exchange
        self.exchange_ccxt = ccxt.binance()
    

if __name__ == "__main__":
    import datetime
    from backtesting_data.utils.timeframe import intervalToSeconds

    symbol   = 'BTC/USDT'
    interval = '5m'
    limit    = 10
    end_time = datetime.datetime(2024, 10, 25, 20, 30)
    secgs = intervalToSeconds(interval)
    
    start_time = int( (end_time.timestamp()-(secgs*(limit+1))) *1000)  
    end_time   = int( (end_time.timestamp()) *1000)

    tmp = binance_spot(None, None)
    
    test = tmp.findKline(
            symbol,
            interval,
            start_time=start_time, 
            end_time=end_time, 
            #limit=limit
    )
    print(test)
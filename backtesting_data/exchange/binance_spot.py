from backtesting_data.utils.exchange_data import exchange_data
from backtesting_data.utils.timeframe import xToTimestampMil
import datetime
import hashlib

from binance.api import API
from binance.lib.utils import check_required_parameters

class api_binance_spot(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://data-api.binance.vision"
        super().__init__(key, secret, **kwargs)

    def klines(self, symbol: str, interval: str, **kwargs):
        """
        |
        | **Kline/Candlestick Data**
        | *Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.*

        :API endpoint: ``GET /api/v3/klines``
        :API doc: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/public-api-endpoints#klinecandlestick-data

        :parameter symbol: string; the trading pair
        :parameter interval: string; the interval of kline, e.g 1m, 5m, 1h, 1d, etc. (see more in https://developers.binance.com/docs/derivatives/coin-margined-futures/common-definition)
        :parameter limit: optional int; limit the results. Default 500, max 1000.
        :parameter startTime: optional int; Timestamp in ms to get aggregate trades from INCLUSIVE.
        :parameter endTime: optional int; Timestamp in ms to get aggregate trades until INCLUSIVE.
        :parameter timeZone: optional str; Default: 0 (UTC)
        |
        """

        check_required_parameters([[symbol, "symbol"], [interval, "interval"]])
        params = {"symbol": symbol, "interval": interval, **kwargs}
        return self.query("/api/v3/klines", params)

class binance_spot(exchange_data):
    _col_name_index = 'Index'
    _cols_kline = {
        'Index': 0,
        'Open': 1,
        'Close': 4,
        'High': 2,
        'Low': 3,
        'Volume': 7,
    }
    
    limit_kline = 1000
    
    def __init__(self, cache_path=None, cache_type=None):
        super().__init__(cache_path=cache_path, cache_type=cache_type)
        self._cache_path_exchange = 'binance_spot'
        self.public_name:str=self._cache_path_exchange
        self._api = api_binance_spot()
    
    def findKline(self, symbol, interval, start_time=None, end_time=None, limit=500) -> list:
        #limit_orig = limit
        if limit > self.limit_kline:
            limit = self.limit_kline
            self.logger.warning("Limit is greater than 1000, setting limit to 1000")
        if start_time is None and end_time is None:
            return self.__findKline(symbol, interval, limit=limit)

        attrs = {
            'symbol': symbol,
            'interval': interval, 
            'limit': limit,
        }
        
        if start_time is not None:
            try:
                attrs['start_time'] = xToTimestampMil(start_time)
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise ValueError("Invalid start_time type")
            
        if end_time is not None:
            # try:
            #     attrs['end_time'] = xToTimestampMil(end_time)
            # except Exception as e:
            #     self.logger.error(f"Error: {e}")
            #     raise ValueError("Invalid start_time type")

            end_time   = datetime.datetime.fromtimestamp(int(xToTimestampMil(end_time)/1000))
        else:
            if start_time is not None:
                end_time   = datetime.datetime.fromtimestamp(int(attrs['start_time']/1000))

        hist=[]
        last_primero_time=None
        while True:
            
            # print('while start Time: ', datetime.datetime.fromtimestamp(int(attrs['start_time']/1000)))
            tmp = self.__findKline(**attrs)
            hist.append(tmp)

            primero = tmp[ len(tmp)-1 ]
            primero_time = datetime.datetime.fromtimestamp(int(primero[self._col_name_index]/1000))
            
            
            if primero_time.timestamp() < end_time.timestamp() and last_primero_time != primero_time:
                attrs['start_time'] = xToTimestampMil(primero_time)
                last_primero_time=primero_time
                continue
            break
        return self.union_lots(hist)
                

    def __findKline(self, symbol, interval, start_time=None, end_time=None, limit=500):

        attrs = {
            'symbol': symbol,
            'interval': interval, 
            'limit': limit,
        }
        if start_time is not None:
            try:
                attrs['startTime'] = xToTimestampMil(start_time)
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise ValueError("Invalid start_time type")
        if end_time is not None:
            try:
                attrs['endTime'] = xToTimestampMil(start_time)
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise ValueError("Invalid start_time type")
        
        key = hashlib.md5(str(attrs).encode()).hexdigest()

        _cache = self.validCache('findKline', key, 3300)
        if _cache is False:
            _cache = self._api.klines(**attrs)
            self.setCache('findKline', key, _cache)

        return _cache

if __name__ == "__main__":
    from backtesting_data.utils.timeframe import xToTimestampMil, intervalToSeconds    
    symbol   = 'BTCUSDT'
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
            limit=limit
    )
    print(test)
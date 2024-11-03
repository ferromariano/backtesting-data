from backtesting_data.utils.exchange_data import exchange_data
from backtesting_data.utils.timeframe import xToTimestampMil
import datetime
import hashlib
from binance.cm_futures import CMFutures

class binance_futures_cm(exchange_data):
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
        self._cache_path_exchange = 'binance_futures_cm'
        self.public_name:str=self._cache_path_exchange
        self._api = CMFutures()
    
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
            primero_time = datetime.datetime.fromtimestamp(int(primero[0]/1000))
            
            
            if primero_time.timestamp() < end_time.timestamp() and last_primero_time != primero_time:
                attrs['start_time'] = xToTimestampMil(primero_time)
                last_primero_time=primero_time
                continue
            break
        return self.union_lots(hist)

        rs = {}
        for lote in hist:
            for i in lote:
                if i[0] not in rs:
                    rs[i[ self._cols_kline['Index'] ]] = {}
                    for key, _col in self._cols_kline.items():
                        if key == 'Index':
                            rs[i[0]][key] = int( int(i[_col]) / 1000 )
                        elif key in ['Open', 'Close', 'High', 'Low', 'Volume']:
                            rs[i[0]][key] = float(i[_col])
                    #rs[i[0]] = i
        
        
        return list(rs.values())
                

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
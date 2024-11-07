import datetime
import pandas as pd
from backtesting_data.utils.exchange_data import exchange_data

class exchange_ccxt_data(exchange_data):

    def findKline(self, symbol, interval, start_time=None, end_time=None, limit=None) -> list:
        _start_time_fnd = datetime.datetime.now()
        _end_time = None
        limit_max = 1000
        params = {
            'symbol': symbol,
            'timeframe': interval,
            'params': {}
        }
        
        if start_time is not None: 
            params['since'] = start_time
        if end_time is not None: 
            params['params']['until'] = end_time
            _end_time = datetime.datetime.fromtimestamp(end_time/1000)
        if limit is not None: 
            params['limit'] = limit if limit < limit_max else limit_max
        
        
        
        hist = pd.DataFrame()
        while True:
            data = self.exchange_ccxt.fetch_ohlcv(**params)
            
            if len(data) == 0:
                break
            _pd_data = pd.DataFrame( data, columns=self._cols_kline.keys() )
            
            
            hist = pd.concat([hist, _pd_data], ignore_index=True)
            
            
            last_time = datetime.datetime.fromtimestamp(data[-1][self._cols_kline['Index']]/1000)
            
            if _start_time_fnd < last_time or _start_time_fnd.timestamp() - last_time.timestamp() < 60:
                break
            
            if _end_time is None:
                if len(hist) >= limit:
                    params['since'] = data[-1][self._cols_kline['Index']]
                    continue
            else:
                if last_time < _end_time:
                    params['since'] = data[-1][self._cols_kline['Index']]
                    continue
            
            
            
            break
        hist.drop_duplicates(inplace=True)

        return self.parce_lot(data)

    def parce_lot(self, lot):
        rs = {}
        for i in lot:
            if i[ self._cols_kline['Index'] ] not in rs:
                rs[i[ self._cols_kline['Index'] ]] = {}
                for key, _col in self._cols_kline.items():
                    if key == 'Index':
                        rs[i[self._cols_kline['Index']]][key] = int(i[_col])
                    elif key in ['Open', 'Close', 'High', 'Low', 'Volume']:
                        rs[i[self._cols_kline['Index']]][key] = float(i[_col])
        
        return list(rs.values())


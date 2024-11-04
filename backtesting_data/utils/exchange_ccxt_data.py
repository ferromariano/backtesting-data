from backtesting_data.utils.exchange_data import exchange_data

class exchange_ccxt_data(exchange_data):

    def findKline(self, symbol, interval, start_time=None, end_time=None, limit=None) -> list:
        params = {
            'symbol': symbol,
            'timeframe': interval,
            'params': {}
        }
        
        if start_time is not None: 
            params['since'] = start_time
        if end_time is not None: 
            params['params']['until'] = end_time
        if limit is not None: 
            params['limit'] = limit
                
        data = self.exchange_ccxt.fetch_ohlcv(**params)

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


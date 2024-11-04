import os
import logging
import time

import base64
import string

class exchange_data:

    _default_cache_path:str = './.cache/backtesting_data'
    _default_cache_type:str = 'csv'
    _col_name_index = 'Index'
    _cols_kline_names = [ 'Index', 'Open', 'Close', 'High', 'Low', 'Volume' ]


    logger = logging.getLogger('managerDbKline')
    logger.setLevel(logging.INFO)

    def __init__(self, cache_path=None, cache_type=None):
        self.public_name:str='exchange_data'
        self._cache_path_exchange:str='exchange_data'

        self._historial_cache={}

        self._cache_path = cache_path if cache_path else exchange_data._default_cache_path
        self._cache_type = cache_type if cache_type else exchange_data._default_cache_type
        
    @property
    def cache_type(self) -> str:
        return self._cache_type

    @property
    def cache_path_exchange(self) -> str:
        dir_path = f"{self._cache_path}/{self._cache_path_exchange}"
        if not os.path.isdir(dir_path):
            os.makedirs( dir_path, exist_ok=True )
        return dir_path

    def get_path_file(self, symbol: str, interval: str) -> str:


        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        _symbol = ''.join(c for c in symbol if c in valid_chars)
        return f"{self.cache_path_exchange}/{_symbol}_{interval}.{self._cache_type}"


    def hasInCache(self, fnd, key):
        if fnd not in self._historial_cache:
            self._historial_cache[fnd] = {}
        if key not in self._historial_cache[fnd]:
            self._historial_cache[fnd][key] = { 'time': None, 'value': None }
            return False
        if self._historial_cache[fnd][key]['time'] is None:
            return False
        return True

    def validCache(self, fnd, key, cache_expired=10):
        if self.hasInCache(fnd, key):
            if time.time() - self._historial_cache[fnd][key]['time'] < cache_expired:
                return self._historial_cache[fnd][key]['value']
        return False

    def setCache(self, fnd, key, value):
        self._historial_cache[fnd][key] = { 'time': time.time(), 'value': value }
        return True
    
    def union_lots(self, hist):
        rs = {}
        for lote in hist:
            for i in lote:
                if i[ self._cols_kline['Index'] ] not in rs:
                    rs[i[ self._cols_kline['Index'] ]] = {}
                    for key, _col in self._cols_kline.items():
                        if key == 'Index':
                            rs[i[self._cols_kline['Index']]][key] = int(i[_col])
                        elif key in ['Open', 'Close', 'High', 'Low', 'Volume']:
                            rs[i[self._cols_kline['Index']]][key] = float(i[_col])
        
        return list(rs.values())

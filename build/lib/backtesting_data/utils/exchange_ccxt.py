import ccxt
from backtesting_data.utils.exchange_ccxt_data import exchange_ccxt_data

class exchange_ccxt(exchange_ccxt_data):
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

    def setExchangeName(self, name):
        self._cache_path_exchange = name
        self.public_name:str=self._cache_path_exchange
        
        if hasattr(ccxt, name) and callable(getattr(ccxt, name)):
            _exchange = getattr(ccxt, name)
            self.exchange_ccxt = _exchange()
            return

        raise AttributeError(f"{name} exchange no fue encontrado")

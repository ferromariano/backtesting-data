from backtesting_data.history import historySymbol


## binance_futures_cm
binance_futures_cm_data = historySymbol('binance_futures_cm', 'ETHUSD_PERP',  interval='1m', limit=10)
print('binance_futures_cm')
binance_futures_cm_data.info()
print(binance_futures_cm_data.head())


## binance_futures
binance_futures_data    = historySymbol('binance_futures',    'BTCUSDT', interval='1m', limit=10)
print('binance_futures')
binance_futures_data.info()
print(binance_futures_data.head())


## binance_spot
binance_spot_data       = historySymbol('binance_spot',       'BTCUSDT', interval='1m', limit=10)
print('binance_spot')
binance_spot_data.info()
print(binance_spot_data.head())


## bingx_futures
bingx_futures_data      = historySymbol('bingx',      'BTC/USDT:USDT', interval='1m', limit=10)
print('bingx_futures')
bingx_futures_data.info()
print(bingx_futures_data.head())


## bingx_spot
bingx_spot_data         = historySymbol('bingx',         'BTC/USDT', interval='1m', limit=10)
print('bingx_spot')
bingx_spot_data.info()
print(bingx_spot_data.head())



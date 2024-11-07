from backtesting_data.history import historySymbol

exchange_name = 'binanceus'
## binance_spot
binance_spot_data       = historySymbol(exchange_name, 'BTCUSDT', interval='1m', limit=100)
print(exchange_name)
binance_spot_data.info()
print(binance_spot_data.head())


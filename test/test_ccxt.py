import ccxt
import pprint
import time


name = 'bingx'

pprint.pprint(hasattr(ccxt, name) and callable(getattr(ccxt, name)))

exchange = getattr(ccxt, name)


exchange()



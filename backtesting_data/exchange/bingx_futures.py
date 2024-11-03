import requests
from backtesting_data.utils.exchange_data import exchange_data
from backtesting_data.utils.timeframe import xToTimestampMil
import datetime
import hashlib
import logging
import json
from json import JSONDecodeError
import time
from urllib.parse import urlencode


def check_required_parameter(value, name):
    if not value and value != 0:
        raise ValueError(f"ParameterRequiredError {name}") 
def check_required_parameters(params):
    """validate multiple parameters
    params = [
        ['btcusdt', 'symbol'],
        [10, 'price']
    ]

    """
    for p in params:
        check_required_parameter(p[0], p[1])
def cleanNoneValue(d) -> dict:
    out = {}
    for k in d.keys():
        if d[k] is not None:
            out[k] = d[k]
    return out
def encoded_string(query, special=False):
    if special:
        return urlencode(query).replace("%40", "@").replace("%27", "%22")
    else:
        return urlencode(query, True).replace("%40", "@")
class api_bingx_futures(object):
    def __init__(self, key=None, secret=None, **kwargs):
        self.base_url = "https://open-api.bingx.com"
        self.proxies = None
        self.timeout = None
        self.show_limit_usage = False
        self.session = requests.Session()
        self.show_header = False

    def klines(self, symbol: str, interval: str, **kwargs):
        """
        |
        | **Kline/Candlestick Data**
        | *Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.*

        :API endpoint: ``GET /openApi/swap/v3/quote/klines``
        :API doc: https://bingx-api.github.io/docs/#/en-us/swapV2/market-api.html#Kline%2FCandlestick%20Data

        :parameter symbol: string; the trading pair
        :parameter interval: string; the interval of kline, e.g 1m, 5m, 1h, 1d, etc. 
        :parameter startTime: optional int; Timestamp in ms to get aggregate trades from INCLUSIVE.
        :parameter endTime: optional int; Timestamp in ms to get aggregate trades until INCLUSIVE.
        :parameter limit: optional int; limit the results. Default 500, max 1000.
        :parameter recvWindow: optional int64; Timestamp of initiating the request, Unit: milliseconds
        :parameter timestamp: optional int64; Request valid time window value, Unit: milliseconds
        |
        """

        check_required_parameters([[symbol, "symbol"], [interval, "interval"]])
        params = {"symbol": symbol, "interval": interval, **kwargs}
        return self.query("/openApi/swap/v3/quote/klines", params)

    def query(self, url_path, payload=None):
        return self.send_request("GET", url_path, payload=payload)

    def send_request(self, http_method, url_path, payload=None, special=False):
        if payload is None:
            payload = {}
        url = self.base_url + url_path
        logging.debug("url: " + url)
        params = cleanNoneValue(
            {
                "url": url,
                "params": self._prepare_params(payload, special),
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        response = self.session.get(**params)
        logging.debug("raw response from server:" + response.text)
        self._handle_exception(response)

        try:
            data = response.json()
        except ValueError:
            data = response.text
        result = {}

        if self.show_limit_usage:
            limit_usage = {}
            for key in response.headers.keys():
                key = key.lower()
                if (
                    key.startswith("x-mbx-used-weight")
                    or key.startswith("x-mbx-order-count")
                    or key.startswith("x-sapi-used")
                ):
                    limit_usage[key] = response.headers[key]
            result["limit_usage"] = limit_usage

        if self.show_header:
            result["header"] = response.headers

        if len(result) != 0:
            result["data"] = data
            return result

        return data

    def _prepare_params(self, params, special=False):
        return encoded_string(cleanNoneValue(params), special)

    def _handle_exception(self, response):
        status_code = response.status_code
        if status_code < 400:
            return
        if 400 <= status_code < 500:
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise  ValueError(f"ClientError({status_code}, None, {response.text}, {response.headers})")   
            raise      ValueError(f"ClientError({status_code}, {err['code']}, {err['msg']}, {response.headers})")   
        raise          ValueError(f"ServerError({status_code}, {response.text})")   

class bingx_futures(exchange_data):
    _col_name_index = 'Index'
    _cols_kline = {
        'Index': 'time',
        'Open': 'open',
        'Close': 'close',
        'High': 'high',
        'Low': 'low',
        'Volume': 'volume',
    }
    
    limit_kline = 1000
    
    alias = {
        'BTCUSDT': 'BTC-USDT',
    }
    
    def __init__(self, cache_path=None, cache_type=None):
        super().__init__(cache_path=cache_path, cache_type=cache_type)
        self._cache_path_exchange = 'bingx_futures'
        self.public_name:str=self._cache_path_exchange
        self._api = api_bingx_futures()
    
    def findKline(self, symbol, interval, start_time=None, end_time=None, limit=500) -> list:
        #limit_orig = limit
        if limit > self.limit_kline:
            limit = self.limit_kline
            self.logger.warning("Limit is greater than 1000, setting limit to 1000")
        if start_time is None and end_time is None:
            return self.__findKline(symbol, interval, limit=limit)
        
        if symbol in self.alias:
            self.logger.warning(f"Alias symbol detected {symbol} to {self.alias[symbol]}")
            symbol = self.alias[symbol]

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
            if 'code' in tmp:
                if tmp['code'] == 0:
                    hist.append(tmp['data'])

                    primero = tmp['data'][ len(tmp['data'])-1 ]
                    primero_time = datetime.datetime.fromtimestamp(int(primero[ self._cols_kline[self._col_name_index] ]/1000))
                    
                    if primero_time.timestamp() < end_time.timestamp() and last_primero_time != primero_time:
                        attrs['start_time'] = xToTimestampMil(primero_time)
                        last_primero_time=primero_time
                        continue
                else:
                    self.logger.error(f"BINGX RESPONCE Error: {tmp['msg']}")
                    raise TypeError(f"BINGX RESPONCE Error: {tmp['msg']}")
                    break
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



    tmp = bingx_futures(None, None)
    
    test = tmp.findKline(
            symbol,
            interval,
            start_time=start_time, 
            end_time=end_time, 
            limit=limit
    )
    for i in test:
        print(i)
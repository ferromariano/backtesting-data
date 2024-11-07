import os
import datetime
from backtesting_data.utils.class_loader import ClassLoader
from backtesting_data.utils.exchange_ccxt import exchange_ccxt
from backtesting_data.utils.timeframe import xToTimestampMil, intervalToSeconds
import logging
from backtesting_data.utils.exchange_data import exchange_data

import io

import pandas as pd
import numpy as np
from typing import Dict

class ManagerDbKlineExchange():
    _db:Dict[str, Dict[str, pd.DataFrame]] = {}

    def __init__(self, exchange: exchange_data, logger: logging.Logger, cache:bool=True):
        self.exchange:exchange_data = exchange
        self.logger = logger
        self.cache = cache

    def _setDb( self, symbol: str, interval: str, _data: pd.DataFrame):
        
        self.logger.debug(f"_setDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'init')

        if symbol not in self._db:
            self._db[symbol] = {}
        self._db[symbol][interval] = _data
        self.logger.debug(f"_setDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'end')

        return self

    def _getDb( self, symbol: str, interval: str, generate=True, load_cache=True) -> pd.DataFrame:
        
        self.logger.debug(f"_getDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'init')

        if symbol not in self._db:
            if generate:
                self._db[symbol] = {}
            else:
                self.logger.debug(f"_getDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'end - no se encontro el simbolo')
                return None
        if interval not in self._db[symbol]:
            if generate:
                self._db[symbol][interval] = pd.DataFrame( columns=exchange_data._cols_kline_names)
                self._db[symbol][interval].set_index(exchange_data._col_name_index, drop=False, inplace=True)
            else:
                self.logger.debug(f"_getDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'end - no se encontro el intervalo')
                return None
        self.logger.debug(f"_getDb({self.exchange.public_name}, {symbol}, {interval}) %s", 'end')
        return self._db[symbol][interval]

    def unifique2DataFrame( self, pd1: pd.DataFrame, pd2: pd.DataFrame ) -> pd.DataFrame:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("unifique2DataFrame %s", 'init')
            buf = io.StringIO()
            pd1.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"pd1: {(buf.getvalue())}")

            buf = io.StringIO()
            pd2.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"pd2: {(buf.getvalue())}")
        pd1.reset_index(drop = True, inplace = True)
        pd2.reset_index(drop = True, inplace = True)

        if len(pd1) == 0:
            pdTemp=pd2
        elif len(pd2) == 0:
            pdTemp=pd1
        else:
            pd1.set_index(exchange_data._col_name_index, inplace=True, drop=False)
            pd2.set_index(exchange_data._col_name_index, inplace=True, drop=False)

            pdTemp = pd1.combine_first(pd2)

        if self.logger.isEnabledFor(logging.DEBUG):
            buf = io.StringIO()
            pdTemp.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"unifique2DataFrame\n {(buf.getvalue())} %s", 'end')
        
        return pdTemp

    def _prepareIncludeData( self, symbol: str, interval: str, _data: pd.DataFrame) -> pd.DataFrame:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"_prepareIncludeData({self.exchange.public_name}, {symbol}, {interval}) %s", 'init')
            buf = io.StringIO()
            _data.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"{(buf.getvalue())}")

        _data.reset_index( drop = True, inplace = True)
        
        ## elimino columnas extras        
        diff_cols_extras = list(set(_data.columns.to_list()) - set(exchange_data._cols_kline_names))
        _data.drop(columns=diff_cols_extras, inplace=True)
        
        if len(_data):
            _data['symbol'] = symbol
            _data['interval'] = interval
        

        diff_cols_faltantes = list(set(exchange_data._cols_kline_names)-set(_data.columns.to_list()))
        for col in diff_cols_faltantes:
            _data[col] = pd.Series([np.nan]*len(_data), index = _data.index, dtype='float64')
        
        for col in diff_cols_faltantes:
            if col == 'diff_open_close':
                _data['diff_open_close'] = (_data['close'] / (_data['open']/100)) - 100
            elif col == 'diff_open_high':
                _data['diff_open_high'] = (_data['high'] / (_data['open']/100)) - 100
            elif col == 'diff_open_low':
                _data['diff_open_low'] = (_data['low'] / (_data['open']/100)) - 100

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"_prepareIncludeData({self.exchange.public_name}, {symbol}, {interval}) ")
            buf = io.StringIO()
            _data.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"{(buf.getvalue())} %s", 'end')

        return _data

    def _loadContentFileCache( self, symbol: str, interval: str) -> pd.DataFrame:
        
        self.logger.debug(f"_loadContentFileCache({self.exchange.public_name}, {symbol}, {interval}) %s", 'init')

        file = self.exchange.get_path_file(symbol, interval)
        if os.path.isfile(file) and os.path.exists(file):
            try:
                if self.exchange.cache_type == 'json':
                    _data = pd.read_json(file)
                elif self.exchange.cache_type == 'csv':
                    _data = pd.read_csv(file)
                else:
                    raise ValueError("Tipo de cache invalido")

                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"_loadContentFileCache({self.exchange.public_name}, {symbol}, {interval}) %s", 'end')
                    buf = io.StringIO()
                    _data.info(False,show_counts=True, buf=buf)
                    self.logger.debug(f"{(buf.getvalue())} %s", 'end')

                return _data
            except:
                pass
        
        self.logger.debug(f"_loadContentFileCache({self.exchange.public_name}, {symbol}, {interval}) %s", 'clear cache end')
        return self._prepareIncludeData(symbol, interval, pd.DataFrame())

    def savecache( self, symbol: str, interval: str, merge=True):
        self.logger.debug(f"savecache({self.exchange.public_name}, {symbol}, {interval}, {merge}) %s", 'init')
        if self.cache:
            _data = self._getDb(symbol, interval, False)
            if _data is not None:
                if merge:
                    _old_data = self._loadContentFileCache(symbol, interval)
                    _data = self.unifique2DataFrame(_data, _old_data)
                file = self.exchange.get_path_file(symbol, interval)
                if self.exchange.cache_type == 'json':
                    _data.to_json(file, index=False)
                elif self.exchange.cache_type == 'csv':
                    _data.to_csv(file, index=False)
                else:
                    raise ValueError("Tipo de cache invalido")
        else:
            self.logger.debug(f"savecache({self.exchange.public_name}, {symbol}, {interval}, {merge}) %s", 'not cache')
        return self

    def loadcache( self, symbol: str, interval: str, merge=True):
        self.logger.debug(f"loadcache({self.exchange.public_name}, {symbol}, {interval}, {merge}) %s", 'init')
        if self.cache:
            _data = self._loadContentFileCache(symbol, interval)
            if len(_data):
                if merge:
                    return self.addData(symbol, interval, _data)
                return self._setDb(symbol, interval, _data)
        else:
            self.logger.debug(f"loadcache({self.exchange.public_name}, {symbol}, {interval}, {merge}) %s", 'not cache')
        return self

    def loadHistorical( self, symbol: str, interval: str, start_time=None, end_time=None, limit=500):
        
        self.logger.debug(f"loadHistorical({self.exchange.public_name}, {symbol}, {start_time}, {end_time}, {limit}) %s", 'init')

        klines = self.exchange.findKline(
            symbol,
            interval,
            start_time=start_time, 
            end_time=end_time, 
            limit=limit
        )
        
        return self.addData(
            symbol,
            interval,
            klines
        )

    def autoCompleteHistorical( self, symbol: str, interval: str, end_time=None):
        
        self.logger.debug(f"autoCompleteHistorical({self.exchange.public_name}, {symbol}, {interval}, {end_time}) %s", 'init')

        secgs = self._intervalToSeconds(interval)
        
        _pd = self._getDb(symbol, interval, True)
        
        asd = (((_pd['start_time'] - _pd['start_time'].shift(1)) / 1000 ) - secgs) / secgs
        asd.pop(_pd.first_valid_index())
        
        kakak = asd.to_list()
        kakak.append(0)
        
        print(kakak)
        print(_pd['start_time'].tolist())
        
        incompletos = pd.DataFrame(columns=['start_time', 'close_time', 'diff'])
        incompletos['start_time'] = _pd['start_time'].tolist()
        incompletos['close_time'] = _pd['close_time'].tolist()
        incompletos['diff'] = kakak
        incompletos = incompletos[ incompletos['diff'] > 0 ]
        
        self.logger.debug("autoCompleteHistorical incompletos\n %s", f'{incompletos}')

        if len(incompletos):
            for a in incompletos.T.to_dict().values():
                # self.loadHistorical(symbol, interval, start_time=int(a['start_time']), end_time=int(a['close_time']), limit=int(a['diff']))
                self.loadHistorical(symbol, interval, start_time=int(a['start_time']), limit=int(a['diff'])+1)
            self.savecache(symbol, interval)
        
    def addData( self, symbol: str, interval: str, _data):
        
        self.logger.debug(f"addData({self.exchange.public_name}, {symbol}, {interval}) %s", 'init')

        if isinstance(_data, pd.DataFrame):
            origin= self._getDb(symbol, interval, True)
            #####
            _data = self._prepareIncludeData(symbol, interval, _data)
            if len(origin) > 0:
                new_pd = self.unifique2DataFrame(origin, _data)
            else:
                new_pd = self.unifique2DataFrame(pd.DataFrame(columns=exchange_data._cols_kline_names), _data)
                
            self._setDb(symbol, interval, new_pd)
            
            return self
        # elif isinstance(_data, dict):
        #     return self.addData(symbol, interval, pd.DataFrame([_data]))
        elif isinstance(_data, list):
            if len(_data) > 0:
                if isinstance(_data[0], Dict):
                    
                    for _col in self.exchange._cols_kline.keys():
                        if _col not in _data[0]:
                            raise ValueError("Datos invalidos: no se encontraron la columna {_col}")
                    
                    _df = pd.DataFrame(_data)
                    _df.set_index(self.exchange._col_name_index, drop=False, inplace=True)
                    return self.addData(symbol, interval, _df)
                raise ValueError("Datos invalidos: lista del tipo "+str(type(_data[0])))
            return self
            

        raise ValueError("Invalid data type")

    def getData( self, symbol: str, interval: str, start_time:int, end_time=None, limit=50, onlyDb=False, _self_origin=False) -> pd.DataFrame:
        
        self.logger.debug(f"getData(symbol:{symbol}, interval:{interval}, start_time:{start_time}, end_time:{end_time}, limit:{limit}, _self_origin:{_self_origin}) %s",'init')

        
        _db = self._getDb(symbol, interval, True)
        if end_time is None:
            pd_filter = _db[(_db[exchange_data._col_name_index] >= start_time)]
            if len(pd_filter):
                secgs = self._intervalToSeconds(interval)
                if (pd_filter['start_time'][ pd_filter.first_valid_index() ]-start_time) > secgs*1000:
                    pd_filter=[]
        else:
            pd_filter = _db[(_db[exchange_data._col_name_index] >= start_time) & (_db[exchange_data._col_name_index] <= end_time)]
        
        if len(pd_filter) < limit and not _self_origin and not onlyDb:
            self.loadHistorical(symbol, interval, start_time=start_time, end_time=end_time, limit=limit)
            pd_filter = self.getData(symbol, interval, start_time=start_time, end_time=end_time, limit=limit, _self_origin=True)
            

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"_loadContentFileCache({self.exchange.public_name}, {symbol}, {interval}) %s", 'end')
            buf = io.StringIO()
            pd_filter.info(False,show_counts=True, buf=buf)
            self.logger.debug(f"getData\n {(buf.getvalue())} %s", 'end')

        return pd_filter

    def getDatatoEnd( self, symbol, interval='5m', limit=100, end_time=None ):
        if end_time is not None:
            datetimeNow = end_time.timestamp()
        else:
            datetimeNow = datetime.datetime.now().timestamp()
        secgs = intervalToSeconds(interval)
        #datetimeNow -= secgs*5
        start_time = int( (datetimeNow-(secgs*(limit+1))) *1000)  
        end_time   = int( (datetimeNow) *1000)
        
        self.loadcache(symbol, interval)
        
        data:pd.DataFrame = self.getData(symbol, interval, start_time=start_time, end_time=end_time, limit=limit)
        
        self.savecache(symbol, interval)
        
        #cols_drop = ['close_time', 'diff_open_close', 'diff_open_high', 'diff_open_low', 'fidatat_trade_ID', 'interval', 'is_closed', 'last_trade_ID', 'n_trades', 'symbol', 'volume_base_asset', 'volume_quote_asset', 'volume_taker_buy_quote' ]
        #col_rename = {'start_time': 'Start_time', 'close': 'Close', 'open': 'Open', 'high': 'High', 'low': 'Low', 'volume_taker_buy_base': 'Volume'}
        #data.rename(columns=col_rename, inplace=True)
        data.reset_index(inplace=True, drop=True)
        data[exchange_data._col_name_index] = pd.to_datetime(data[exchange_data._col_name_index], unit='ms')
        data.set_index(exchange_data._col_name_index, inplace=True, drop=True)
        
        return data

class ManagerDbKline():
    cache_path:str = './.cache/backtesting_data/'
    cache_type:str = 'csv'
    
    logger = logging.getLogger('managerDbKline')
    logger.setLevel(logging.INFO)
    
    _cache_exchange = {}
    _class_loader:ClassLoader = ClassLoader("backtesting_data/exchange")
    
    def getExchange( exchange_name: str, cache=True) -> ManagerDbKlineExchange:
        if exchange_name not in ManagerDbKline._cache_exchange:
            try:
                exchange_class = ManagerDbKline._class_loader.load_class(exchange_name)
                _exchange_attr = {
                    'cache_path': ManagerDbKline.cache_path,
                    'cache_type': ManagerDbKline.cache_type,
                }
                _exchange = exchange_class(**_exchange_attr)
            except (FileNotFoundError, ImportError, AttributeError) as e:
                try:
                    _exchange = exchange_ccxt()
                    _exchange.setExchangeName(exchange_name)
                except (FileNotFoundError, ImportError, AttributeError) as e:
                    raise e

            ManagerDbKline._cache_exchange[exchange_name] = ManagerDbKlineExchange(exchange=_exchange, logger=ManagerDbKline.logger, cache=cache)
        
        return ManagerDbKline._cache_exchange[exchange_name]


    


if __name__ == "__main__":

    exchange:ManagerDbKlineExchange = ManagerDbKline.getExchange('binance_spot', True)
    
    end_time = datetime.datetime(2024, 10, 25, 20, 30)

    tmp = exchange.getDatatoEnd(
        'BTCUSDT',
        '1m',
        10,
        end_time
    )





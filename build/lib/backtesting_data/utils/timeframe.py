import datetime
import numpy as np

def intervalToSeconds( interval: str) -> int:
    if interval == '1m':
        return 60
    elif interval == '3m':
        return 180
    elif interval == '5m':
        return 300
    elif interval == '15m':
        return 900
    elif interval == '30m':
        return 1800
    elif interval == '1h':
        return 3600
    elif interval == '2h':
        return 7200
    elif interval == '4h':
        return 14400
    elif interval == '6h':
        return 21600
    elif interval == '8h':
        return 28800
    elif interval == '12h':
        return 43200
    elif interval == '1d':
        return 86400
    elif interval == '3d':
        return 259200
    elif interval == '1w':
        return 604800
    elif interval == '1M':
        return 2592000
    else:
        raise ValueError("Intervalo invalido")
    
def xToTimestampMil(_expre) -> int:
    if isinstance(_expre, int):
        _expre = _expre
    elif isinstance(_expre, datetime.datetime):
        _expre = int(_expre.timestamp())
    elif isinstance(_expre, datetime.timedelta):
        _expre = int(_expre.total_seconds())
    elif isinstance(_expre, np.int64):
        _expre = int(_expre)
    else:
        raise ValueError("Invalid start_time type")

    if _expre < 10000000000:
        _expre = _expre * 1000
    
    return _expre

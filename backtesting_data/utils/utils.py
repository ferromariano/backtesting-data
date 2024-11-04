import numpy as np
import datetime

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


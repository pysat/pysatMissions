"""
Handles the default pysat functions for simulated instruments
"""

import datetime as dt
import pandas as pds


def _list_files(tag=None, inst_id=None, data_path=None, format_str=None):
    """Produce a fake list of files spanning a year"""

    index = pds.date_range(dt.datetime(2017, 12, 1),
                           dt.datetime(2018, 12, 1))
    # file list is effectively just the date in string format - '%D' works
    # only in Mac. '%x' workins in both Windows and Mac
    names = [data_path + date.strftime('%Y-%m-%d') + '.nofile'
             for date in index]
    return pds.Series(names, index=index)


def _download(date_array, tag, inst_id, data_path=None):
    """ Data is simulated so no download routine is possible. Simple pass
    function"""

    pass




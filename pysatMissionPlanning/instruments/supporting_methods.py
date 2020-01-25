"""
handles the default pysat functions for simulated instruments
"""

import pandas as pds
import pysat


def list_files(tag=None, sat_id=None, data_path=None, format_str=None):
    """Produce a fake list of files spanning a year"""

    index = pds.date_range(pysat.datetime(2017, 12, 1),
                           pysat.datetime(2018, 12, 1))
    # file list is effectively just the date in string format - '%D' works
    # only in Mac. '%x' workins in both Windows and Mac
    names = [data_path + date.strftime('%Y-%m-%d') + '.nofile'
             for date in index]
    return pysat.Series(names, index=index)


def download(date_array, tag, sat_id, data_path=None):
    """ Data is simulated so no download routine is possible. Simple pass
    function"""
    pass

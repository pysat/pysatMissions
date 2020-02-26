"""
Handles the default pysat functions for simulated instruments
"""

import os
import pandas as pds
import pysat


def _list_files(tag=None, sat_id=None, data_path=None, format_str=None):
    """Produce a fake list of files spanning a year"""

    index = pds.date_range(pysat.datetime(2017, 12, 1),
                           pysat.datetime(2018, 12, 1))
    # file list is effectively just the date in string format - '%D' works
    # only in Mac. '%x' workins in both Windows and Mac
    names = [data_path + date.strftime('%Y-%m-%d') + '.nofile'
             for date in index]
    return pysat.Series(names, index=index)


def _download(date_array, tag, sat_id, data_path=None):
    """ Data is simulated so no download routine is possible. Simple pass
    function"""
    pass


def _get_times(fnames, sat_id):
    """Construct list of times for simulated instruments"""

    # grab date from filename
    parts = os.path.split(fnames[0])[-1].split('-')
    yr = int(parts[0])
    month = int(parts[1])
    day = int(parts[2][0:2])
    date = pysat.datetime(yr, month, day)

    # create timing at 1 Hz (defaults to 1 day)
    # Allow numeric string to set number of time steps
    num = 86399 if sat_id == '' else int(sat_id)
    times = pds.date_range(start=date, end=date+pds.DateOffset(seconds=num),
                           freq='1S')

    return times

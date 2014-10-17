__author__ = 'nickroth'

import numpy as np
from pdftables import get_tables
import pandas as pd


def parse_laptimes(filepath):
    """
    Parses a PDF of qualifying or practice report lap times from the FIA into data that we can further analyze. See
    an example at `Japan Qualifying Report <http://www.fia.com/sites/default/files/championship/event_report/documents/2014_15_JPN_F1_Q0_Timing_QualifyingSessionLapTimes_V01.pdf>`_.

    :param filepath: a string pathname to the pdf on your local computer
    :return: - a pandas dataframe with column for number, name, and times
    """

    # open the file
    with open(filepath, 'rb') as fileobj:

        names = []
        nums = []
        times = []

        tables = get_tables(fileobj)

        # loop over each page/table that were parsed out, and append drivers into one list
        for table in tables:
            this_drivers = get_drivers(table)
            for driver in this_drivers:
                # drivers.append(driver)

                h = len(driver['times'])
                this_names = [driver['name']] * h
                this_num = [int(driver['num'])] * h

                names.extend(this_names)
                nums.extend(this_num)
                times.extend(driver['times'])

        # create pandas dataframe
        nums = np.asarray(nums)
        names = np.asarray(names)
        times = np.asarray(times)
        drivers = pd.DataFrame({'driver_no':nums, 'name':names, 'time':times})

        return drivers


def get_drivers(table):
    """
    Takes an input of a pdftable, corresponding to the data on one page of fia lap timing report from qualifications
    or practice. See `Japan Qualifying Report`_ for an example PDF that this function helps parse.

    :param table: pdftable from calling :py:func:`~formulapy.data.fia.parsers.parse_laptimes`
    :return: - list of python dicts, where each dict represents one driver on this page
    """

    drivers = []
    driver1, driver2, driver3 = {}, {}, {}

    idx = []
    new_drivers = False

    # loop over each row in table
    for i, row in enumerate(table):

        this_row = np.asarray(row)

        # each table is separated by a row with 'TIME' in it, which has times below it, based on the index of the
        # location of 'TIME' in the row. the index can change from table to table
        vals = this_row == unicode('TIME')
        if np.any(vals):
            idx = vals

            # search around where we think the driver row will be
            driver_row_idx = None
            for driver_idx in xrange(-3, 4, 1):
                this_driver_row = table[i + driver_idx]

                # make sure not row with times in it, or completely empty row, or the row with TIME in it
                if (sum([1 for x in this_driver_row if ':' in x]) == 0 and len(''.join(this_driver_row)) > 0
                    and driver_idx is not 0):
                    driver_row_idx = driver_idx

            # the row with driver names
            the_row = table[i + driver_row_idx]

            # find the empty strings, which separates the driver names
            empty_strs = [i for i, x in enumerate(the_row) if x == '']
            driver_strs = []
            for j, val in enumerate(empty_strs):

                # join the strings between the empty strings, which collects any split names
                if j is not 0:
                    temp_str = ''.join(the_row[empty_strs[j - 1]:val])
                else:
                    temp_str = ''.join(the_row[0:val])

                # append each joined string to the list
                if temp_str:
                    driver_strs.append(temp_str.replace(' ', ''))

            # split the driver info into their number and name
            driver_strs = [split_num_str(s) for s in driver_strs]

            # set flag that we have found new drivers in the table
            new_drivers = True

        # Only enter this statement after we find the row with 'TIME' in it, which is the primary indicator of a new
        # set of driver information. We hit this the second time through.
        elif np.any(idx):
            the_idx = np.where(idx)
            the_idx = the_idx[0]

            # check for flag telling us we hit a row with driver info in it
            if new_drivers:

                # store out the previous drivers, if this isn't the initial time through
                if 'num' in driver1.keys():
                    drivers.append(driver1)
                if 'num' in driver2.keys():
                    drivers.append(driver2)
                if 'num' in driver3.keys():
                    drivers.append(driver3)

                # reset the drivers flag when we found new driver names
                new_drivers = False

                # reset driver dicts and store in initial new info on the new drivers
                driver1 = init_driver(driver_strs, 0)
                driver2 = init_driver(driver_strs, 1)
                driver3 = init_driver(driver_strs, 2)

            # store the data into the driver information for each of the 3 drivers we handle at a time
            append_time_info(driver1, the_idx, 2, row)
            append_time_info(driver2, the_idx, 4, row)
            append_time_info(driver3, the_idx, 6, row)

    # reached end of drivers for this page, only append the columns/drivers with data
    if 'num' in driver1.keys():
        drivers.append(driver1)
    if 'num' in driver2.keys():
        drivers.append(driver2)
    if 'num' in driver3.keys():
        drivers.append(driver3)

    return drivers


def init_driver(driver_strings, driver_idx):
    """
    Initializes the driver dict and stores values from the driver_strings into it, if they exist

    :param driver_strings: tuple with driver number and name within it
    :param driver_idx: 0, 1, or 2, representing the index of the 3 drivers processed at a time
    :return: initialized driver dict, where empty if there was no info for the given idx
    """

    driver = {}

    if len(driver_strings) >= driver_idx + 1:
        num, name = driver_strings[driver_idx]
        driver['num'] = int(num)
        driver['name'] = str(name)
        driver['times'] = []

    return driver


def append_time_info(driver, idx, pos, row):
    """
    Factors out some common logic for getting the time information for the driver based on their relative position in
    the row.

    :param driver: dict with driver info
    :param idx: the indices of the columns where times should be
    :param pos: the last column that this driver shouldn't have values past
    :param row: the current row being processed
    :return: None, driver dicts are modified directly, so no return required
    """

    if idx is not None and len(idx) >= pos:
        d_list = driver['times']

        # first column for this driver
        if ':' in row[idx[pos - 2]]:
            this_time = format_times(split_joined_times(row[idx[pos - 2]]))
            for t in this_time:
                d_list.append(t)

        # second column for this driver
        if ':' in row[idx[pos - 1]]:
            this_time = format_times(split_joined_times(row[idx[pos - 1]]))
            for t in this_time:
                d_list.append(t)


def split_joined_times(t):
    """
    Splits times that can sometimes be joined together based on how the PDF is formatted. If it doesn't detect joined
    times, then it will just return the single time in a list.

    :param t: a string with likely times in it
    :return: a list containing individual times
    """

    split_times = t.split('.')

    # a single time will split into two pieces
    if len(split_times) > 2:
        mixed = split_times[1]
        time1 = split_times[0] + '.' + mixed[:3]
        time2 = mixed[3:] + '.' + split_times[2]
        times = [time1, time2]
    else:
        times = [t]

    return times


def format_times(t):
    """
    Converts a list of time strings into a list of floats, representing the number of seconds for the given lap.
    Assumes the values are always minutes:seconds.milliseconds.

    :param t: list of time strings
    :return: list of times as floats
    """

    new_t = []

    for time in t:
        time_parts = time.split(':')
        new_t.append(int(time_parts[0]) * 60 + float(time_parts[1]))

    return new_t


def split_num_str(s):
    tail = s.strip('0123456789')
    head = s[:len(s) - len(tail)]
    return head, tail


if __name__ == "__main__":
    filepath = '../../../data/fia_qualifying.pdf'
    drivers = parse_laptimes(filepath)
    print drivers
    print drivers.dtypes
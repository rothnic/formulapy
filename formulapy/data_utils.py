__author__ = 'Nick'


def filter_in_out_laps(data, n_std=3):
    """Filters the in and out laps for each driver.

    Filters the
    """

    gb = data.groupby('driverId')

    no_outliers = lambda x: (
        (x['seconds'] > (x['seconds'].mean() - (x['seconds'].std()*n_std))) &
        (x['seconds'] < (x['seconds'].mean() + (x['seconds'].std()*n_std))))

    return data.ix[gb.apply(no_outliers).reset_index(drop=True, level=0), :]

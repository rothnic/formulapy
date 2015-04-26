__author__ = 'Nick'


def pit_laps(data, n_std=3):
    """Returns a logical vector corresponding to the pit laps for each driver."""
    gb = data.groupby('driverId')

    outliers = lambda x: (
        (x['seconds'] < (x['seconds'].mean() - (x['seconds'].std() * n_std))) |
        (x['seconds'] > (x['seconds'].mean() + (x['seconds'].std() * n_std))))

    return gb.apply(outliers).reset_index(drop=True, level=0)


def filter_pit_laps(data, n_std=3):
    """Filters the in and out laps for each driver."""
    no_pit_laps = ~pit_laps(data, n_std)

    return data.ix[no_pit_laps, :]

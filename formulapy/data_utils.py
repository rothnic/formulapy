__author__ = 'Nick'


def pit_laps(data, time_field='seconds', id_field='driverId', n_std=3):
    """Returns a logical vector corresponding to the pit laps for each driver."""
    gb = data.groupby(id_field)

    outliers = lambda x: (
        (x[time_field] < (x[time_field].mean() - (x[time_field].std() * n_std))) |
        (x[time_field] > (x[time_field].mean() + (x[time_field].std() * n_std))))

    return gb.apply(outliers).reset_index(drop=True, level=0)


def filter_pit_laps(data, time_field='seconds', id_field='driverId', n_std=3):
    """Filters the in and out laps for each driver."""
    no_pit_laps = ~pit_laps(data, time_field=time_field, id_field=id_field, n_std=n_std)

    return data.ix[no_pit_laps, :]

__author__ = 'Nick'

import seaborn as sns
sns.mpl.rcParams['figure.figsize'] = (16, 10)

from formulapy.data_utils import filter_in_out_laps

def lap_box_plot(laps, pit_laps=True):

    if not pit_laps:
        laps = filter_in_out_laps(laps)

    # sort laps by finish order, where not all finish on the last lap
    finish_order = laps.sort(['lap_number', 'position']).groupby(['driverId'],
                                                               as_index=False).last()
    finish_order = finish_order.sort(['lap_number', 'position'], ascending=[False, True])

    ids = reversed(finish_order.driverId.values)
    ids = [str(item) for item in ids]
    return sns.boxplot(laps.seconds, laps.driverId, names=ids, order=ids, vert=False)


def lap_dist_plot(laps, drivers, pit_laps=True):

    if not pit_laps:
        laps = filter_in_out_laps(laps)

    for driver in drivers:
        ax = sns.distplot(laps.ix[laps.driverId == driver, 'seconds'])

    ax.legend(drivers)

    return ax
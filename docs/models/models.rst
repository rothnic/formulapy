.. top level directory for documenting specific models

Models
------

There is a base models package that will provide a generic configuration for specific Tracks, Cars, and Drivers,
as it is possible. These examples are intended to work for most conditions, and will likely be tweaked for a specific
year. An initial example is setup for a generic Spa and a Spa2014 to show how this might work.

Tracks
^^^^^^

.. automodule:: formulapy.models.tracks
    :members:
    :undoc-members:

Seasons
^^^^^^^

Specific season models will go into season-specific packages. The intent is so that someone could get a 2014 version
of Sebastian Vettel and put him in a 2014 car, or they could focus on all time. It is possible that the data could be
weighted differently in each case.

.. toctree::

   s2014


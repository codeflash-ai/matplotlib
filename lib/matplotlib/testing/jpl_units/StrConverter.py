"""StrConverter module containing class StrConverter."""

import numpy as np

import matplotlib.units as units

__all__ = ["StrConverter"]


class StrConverter(units.ConversionInterface):
    """
    A Matplotlib converter class for string data values.

    Valid units for string are:
    - 'indexed' : Values are indexed as they are specified for plotting.
    - 'sorted'  : Values are sorted alphanumerically.
    - 'inverted' : Values are inverted so that the first value is on top.
    - 'sorted-inverted' :  A combination of 'sorted' and 'inverted'
    """

    @staticmethod
    def axisinfo(unit, axis):
        # docstring inherited
        return None

    @staticmethod
    def convert(value, unit, axis):
        # docstring inherited

        if value == []:
            return []

        # we delay loading to make matplotlib happy
        ax = axis.axes
        isXAxis = axis is ax.xaxis

        axis.get_major_ticks()
        ticks = axis.get_ticklocs()
        labels_objs = axis.get_ticklabels()

        # Get nonempty label texts - avoid double list comprehension overhead
        labels = []
        for l in labels_objs:
            txt = l.get_text()
            if txt:
                labels.append(txt)

        if not labels:
            ticks = []
            labels = []

        # Normalize 'value' to a list only if not already an iterable except str
        # str is considered iterable by np.iterable, but in this context, it should be treated as a single value
        if isinstance(value, str) or not np.iterable(value):
            value = [value]

        # Construct labels; use set for O(1) lookup for both labels and newValues
        # labels and newValues preserve input order; use set for lookup only
        labels_set = set(labels)
        newValues = []
        newValues_set = set()
        for v in value:
            if v not in labels_set and v not in newValues_set:
                newValues.append(v)

                newValues_set.add(v)
        labels.extend(newValues)

        # add padding (so they do not appear on the axes themselves)
        labels_padded = [""] + labels + [""]
        ticks = list(range(len(labels_padded)))
        ticks[0] = 0.5
        ticks[-1] = ticks[-1] - 0.5

        axis.set_ticks(ticks)
        axis.set_ticklabels(labels_padded)
        # we have to do the following lines to make ax.autoscale_view work
        # we have to do the following lines to make ax.autoscale_view work
        loc = axis.get_major_locator()
        loc.set_bounds(ticks[0], ticks[-1])

        if isXAxis:
            ax.set_xlim(ticks[0], ticks[-1])
        else:
            ax.set_ylim(ticks[0], ticks[-1])

        # Optimize mapping of value -> tick index using dict
        label_to_tick = {label: tick for label, tick in zip(labels_padded, ticks)}
        result = [label_to_tick[v] for v in value]

        ax.viewLim.ignore(-1)
        return result

    @staticmethod
    def default_units(value, axis):
        # docstring inherited
        # The default behavior for string indexing.
        return "indexed"

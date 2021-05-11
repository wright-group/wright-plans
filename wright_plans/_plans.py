from graphlib import TopologicalSorter

import bluesky.plan_stubs

from ._constants import Constant
from ._units import ureg, get_units

def make_one_nd_step(constants=None, axis_units=None):
    """Generate a one_nd_step function for given metadata.

    The fields taken into account are:
    `axis_units`: a map of motor names to string of pint compatible units
    `constants`: a map of motor names to tuple of (string units, list of (coeff: float, var: string))
    `motors` is a mapping of motor names to motor objects
    """
    if constants is None and axis_units is None:
        # Nothing special to do, just return original method
        return bluesky.plan_stubs.one_nd_step
    if constants is None:
        constants = {}
    if axis_units is None:
        axis_units = {}

    sorter = TopologicalSorter({})
    for var, const in constants.items():
        sorter.add(var, *[x.var for x in const.terms])

    order = [*sorter.static_order()]

    def one_nd_step(detectors, step, pos_cache):
        """Version of bluesky.plan_stubs.one_nd_step with support for constants and units."""
        # Translate axes from scan units to native units
        for mot, units in axis_units.items():
            mot_units = get_units(mot, units)
            quantity = ureg.Quantity(step[mot], units).to(mot_units)
            step[mot] = quantity.magnitude

        # fill out constants in topological order, ignore "", do math in constant's units
        for mot in order:
            if mot not in constants:
                continue
            const = constants[mot]
            const_mot_units = get_units(mot, const.units)
            step[mot] = const.evaluate(step, const_mot_units)
            
        yield from bluesky.plan_stubs.one_nd_step(detectors, step, pos_cache)

    return one_nd_step

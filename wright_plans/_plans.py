from graphlib import TopologicalSorter

import bluesky.plan_stubs
import pint

ureg = pint.UnitRegistry()

ureg.define("wavenumber = 1 / cm = cm^{-1} = wn")

ureg.define("@alias s = s_t")
ureg.define("@alias min = m_t")
ureg.define("@alias hour = h_t")
ureg.define("@alias d = d_t")

ureg.define("@alias degC = deg_C")
ureg.define("@alias degF = deg_F")
ureg.define("@alias degR = deg_R")

ureg.define("@alias m = m_delay")

ureg.enable_contexts("spectroscopy")


# TODO make sure unit retrival is accurate, robust
def get_units(device, default=None):
    return next(iter(device.describe().values())).get("units", default)

def make_one_nd_step(metadata, motors):
    """Generate a one_nd_step function for given metadata.

    The fields taken into account are:
    `axis_units`: a map of motor names to string of pint compatible units
    `constants`: a map of motor names to tuple of (string units, list of (coeff: float, var: string))
    `motors` is a mapping of motor names to motor objects
    """
    print(metadata)
    graph = {k:set() for k in motors.keys()}
    sorter = TopologicalSorter(graph)
    for mot, const in metadata.get("constants", {}).items():
        _, lin_comb = const
        sorter.add(mot, *[x[1] for x in lin_comb])

    order = [*sorter.static_order()]
    print(order)

    def one_nd_step(detectors, step, pos_cache):
        """Version of bluesky.plan_stubs.one_nd_step with support for constants and units."""
        # Translate axes from scan units to native units
        for mot, units in metadata.get("axis_units", {}).items():
            mot_units = get_units(motors[mot], units)
            quantity = ureg.Quantity(step[motors[mot]], units).to(mot_units)
            step[motors[mot]] = quantity.magnitude

        # fill out constants in topological order, ignore "", do math in constant's units
        constants = metadata.get("constants", {})
        for mot in order:
            if mot not in constants:
                continue
            const_units, lin_comb = constants[mot]
            quantity = ureg.Quantity(0, const_units)
            const_mot_units = get_units(motors[mot], const_units)
            for coeff, var in lin_comb:
                if var == "":
                    quantity += ureg.Quantity(coeff, const_units)
                    continue
                mot_units = get_units(motors[var], const_units)
                mot_quantity = ureg.Quantity(step[motors[var]], mot_units).to(const_units)
                mot_quantity *= coeff
                quantity += mot_quantity
            step[motors[mot]] = quantity.to(const_mot_units).magnitude

        yield from bluesky.plan_stubs.one_nd_step(detectors, step, pos_cache)

    return one_nd_step

__all__ = [
    "make_one_nd_step",
    "scan_wp",
    "rel_scan_wp",
    "list_scan_wp",
    "rel_list_scan_wp",
    "list_grid_scan_wp",
    "rel_list_grid_scan_wp",
    "grid_scan_wp",
    "rel_grid_scan_wp",
    "scan_nd_wp",
]

from graphlib import TopologicalSorter

import bluesky.plan_stubs
from bluesky import plans as bsp
from bluesky.protocols import Movable
import toolz

from ._constants import Constant, ConstantTerm
from ._units import ureg, get_units


def make_one_nd_step(constants=None, axis_units=None, per_step=None):
    """Generate a one_nd_step function for given metadata.

    The fields taken into account are:
    `axis_units`: a map of motor names to string of pint compatible units
    `constants`: a map of motor names to tuple of (string units, list of (coeff: float, var: string))
    `motors` is a mapping of motor names to motor objects
    """
    if per_step is None:
        per_step = bluesky.plan_stubs.one_nd_step
    if not constants and not axis_units:
        # Nothing special to do, just return original method
        return per_step
    if not constants:
        constants = {}
    if not axis_units:
        axis_units = {}

    if isinstance(constants, list):
        constants = {
            mot: Constant(units, [ConstantTerm(coeff, var) for coeff, var in terms])
            for mot, units, terms in constants
        }

    sorter = TopologicalSorter({})
    for var, const in constants.items():
        sorter.add(var, *[x.var for x in const.terms])

    order = [*sorter.static_order()]

    def one_nd_step(detectors, step, pos_cache):
        """Version of bluesky.plan_stubs.one_nd_step with support for constants and units."""
        # Translate axes from scan units to native units
        for mot, units in axis_units.items():
            mot_units = get_units(mot, units)
            quantity = ureg.Quantity(step[mot], units)
            if mot_units:
                quantity = quantity.to(mot_units)
            step[mot] = quantity.magnitude

        # fill out constants in topological order, ignore "", do math in constant's units
        for mot in order:
            if mot not in constants:
                continue
            const = constants[mot]
            const_mot_units = get_units(mot, const.units)
            step[mot] = const.evaluate(step, const_mot_units)

        yield from per_step(detectors, step, pos_cache)

    return one_nd_step


def _md_constants(constants):
    if constants is None:
        return {}
    if isinstance(constants, list):
        constants = {
            mot: Constant(units, [ConstantTerm(coeff, var) for coeff, var in terms])
            for mot, units, terms in constants
        }
    return {
        k.name: [
            v.units,
            [[t.coeff, None if t.var is None else t.var.name] for t in v.terms],
        ]
        for k, v in constants.items()
    }


def _axis_units_from_args(args, n):
    return {m: u for m, *_, u in toolz.partition(n, args) if u}


def scan_wp(detectors, *args, num=None, constants=None, per_step=None, md=None):
    nargs = 4
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.scan(detectors, *args, num=num, per_step=per_step, md=_md)


def rel_scan_wp(detectors, *args, num=None, constants=None, per_step=None, md=None):
    nargs = 4
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "rel_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.rel_scan(detectors, *args, num=num, per_step=per_step, md=_md)


def list_scan_wp(detectors, *args, constants=None, per_step=None, md=None):
    nargs = 3
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "list_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.list_scan(detectors, *args, per_step=per_step, md=_md)


def rel_list_scan_wp(detectors, *args, constants=None, per_step=None, md=None):
    nargs = 3
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "rel_list_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.rel_list_scan(detectors, *args, per_step=per_step, md=_md)


def list_grid_scan_wp(
    detectors, *args, constants=None, snake_axes=False, per_step=None, md=None
):
    nargs = 3
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "list_grid_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.list_grid_scan(
        detectors, *args, snake_axes=snake_axes, per_step=per_step, md=_md
    )


def rel_list_grid_scan_wp(
    detectors, *args, constants=None, snake_axes=False, per_step=None, md=None
):
    nargs = 3
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "rel_list_grid_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.rel_list_grid_scan(
        detectors, *args, snake_axes=snake_axes, per_step=per_step, md=_md
    )


def grid_scan_wp(
    detectors, *args, constants=None, snake_axes=False, per_step=None, md=None
):
    nargs = 5
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "grid_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    print(_md)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.grid_scan(
        detectors, *args, snake_axes=snake_axes, per_step=per_step, md=_md
    )


def rel_grid_scan_wp(
    detectors, *args, constants=None, snake_axes=False, per_step=None, md=None
):
    nargs = 5
    axis_units = _axis_units_from_args(args, nargs)
    md_args = [repr(i) if isinstance(i, Movable) else i for i in args]
    _md = {
        "plan_name": "rel_grid_scan_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "args": md_args,
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i, x in enumerate(args) if not i % nargs == nargs - 1]
    yield from bsp.rel_grid_scan(
        detectors, *args, snake_axes=snake_axes, per_step=per_step, md=_md
    )


def scan_nd_wp(
    detectors, cycler, *, axis_units=None, constants=None, per_step=None, md=None
):
    _md = {
        "plan_name": "scan_nd_wp",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "cycler": repr(cycler),
            "axis_units": {k.name: v for k, v in axis_units.items()},
            "constants": _md_constants(constants),
            "per_step": repr(per_step),
        },
        "plan_constants": _md_constants(constants),
        "plan_axis_units": {k.name: v for k, v in axis_units.items()},
    }
    _md.update(md or {})
    per_step = make_one_nd_step(constants, axis_units, per_step)
    yield from bsp.scan_nd(detectors, cycler, per_step=per_step, md=_md)

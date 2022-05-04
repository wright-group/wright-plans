import attune
import numpy as np
from bluesky import Msg
from cycler import cycler

from ._constants import Constant, ConstantTerm
from ._messages import set_relative_to_func_wrapper
from ._plans import scan_nd_wp
from ._units import ureg

def _spectrometer_md(spectrometer):
    if spectrometer is None:
        return None
    spectrometer_md = spectrometer.copy()
    if spectrometer_md.get("device"):
        spectrometer_md["device"] = repr(spectrometer["device"])
    return spectrometer_md

def motortune(detectors, opa, use_tune_points, motors, spectrometer=None, *, md=None):
    cyc = 1
    md = md or {}
    relative_sets = {}
    constants = {}
    axis_units = {}
    shape = []
    pattern_args = []

    scanned_motors = [
        m for m, params in motors.items() if params.get("method") == "scan"
    ]

    if use_tune_points:
        instr = attune.Instrument(**opa.yaq_client.get_instrument())
        arrangement = opa.yaq_client.get_arrangement()
        tune_points = get_tune_points(instr, instr[arrangement], scanned_motors)
        cyc = cycler(opa, tune_points)
        axis_units[opa] = "nm"  # TODO more robust units?
        shape.append(len(tune_points))
        pattern_args.extend([repr(opa), tune_points])
    for mot, params in motors.items():
        if params["method"] == "static":
            cyc *= cycler(getattr(opa, mot), [params["center"]])
        elif params["method"] == "scan":
            if use_tune_points:
                params["center"] = 0

                def _motor_rel(opa, motor):
                    def _motor_rel_inner():
                        return instr(opa.position, arrangement)[motor]

                    return _motor_rel_inner

                relative_sets[getattr(opa, mot)] = {"func": _motor_rel(opa, mot), "native": "", "differential": ""}

            pts = np.linspace(
                params["center"] - params["width"] / 2,
                params["center"] + params["width"] / 2,
                params["npts"],
            )
            cyc *= cycler(getattr(opa, mot), pts)
            shape.append(params["npts"])
            pattern_args.extend([repr(getattr(opa, mot)), pts])
    if spectrometer and spectrometer["device"]:
        if spectrometer["method"] == "static":
            center = ureg.Quantity(spectrometer["center"], spectrometer.get("units", "nm")).to("nm").magnitude
            yield Msg("set", spectrometer["device"], center, group="motortune_prep")
        elif spectrometer["method"] == "zero":
            yield Msg("set", spectrometer["device"], 0, group="motortune_prep")
        elif spectrometer["method"] == "track":
            constants[spectrometer["device"]] = Constant("nm", [ConstantTerm(1, opa)])
        elif spectrometer["method"] == "set":
            if use_tune_points:
                constants[spectrometer["device"]] = Constant(
                    "nm", [ConstantTerm(1, opa)]
                )
            else:
                center = ureg.Quantity(spectrometer["center"], spectrometer.get("units", "nm")).to("nm").magnitude
                yield Msg("set", spectrometer["device"], center, group="motortune_prep")
        elif spectrometer["method"] == "scan":
            if use_tune_points:
                spectrometer["center"] = 0

                def _spec_rel(opa):
                    def _spec_rel_inner():
                        return opa.position

                    return _spec_rel_inner

                relative_sets[spectrometer["device"]] = {"func": _spec_rel(opa), "native": "nm", "differential": spectrometer.get("units", "nm")}
            pts = np.linspace(
                spectrometer["center"] - spectrometer["width"] / 2,
                spectrometer["center"] + spectrometer["width"] / 2,
                spectrometer["npts"],
            )
            cyc *= cycler(spectrometer["device"], pts)
            axis_units[spectrometer["device"]] = spectrometer.get("units", "nm")
            shape.append(spectrometer["npts"])
            pattern_args.extend([repr(spectrometer["device"]), pts])

    yield Msg("wait", None, "motortune_prep")
    local_md = {
        "plan_name": "motortune",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "opa": repr(opa),
            "use_tune_points": use_tune_points,
            "motors": {repr(m): v for m, v in motors.items()},
            "spectrometer": _spectrometer_md(spectrometer),
        },
        "shape": tuple(shape),
        "plan_pattern": "outer_list_product",
        "plan_pattern_module": "bluesky.plan_patterns",
        "plan_pattern_args": {"args": pattern_args},
        "hints": {},
    }
    md = local_md | md
    md["hints"].setdefault("gridding", "rectilinear")
    plan = scan_nd_wp(detectors, cyc, axis_units=axis_units, constants=constants, md=md)
    if relative_sets:
        plan = set_relative_to_func_wrapper(plan, relative_sets)
    return (yield from plan)


def get_tune_points(instrument, arrangement, scanned_motors):
    min_ = arrangement.ind_min
    max_ = arrangement.ind_max
    if not scanned_motors:
        scanned_motors = arrangement.keys()
    inds = []
    for scanned in scanned_motors:
        if scanned in arrangement.keys() and hasattr(
            arrangement[scanned], "independent"
        ):
            inds += [arrangement[scanned].independent]
            continue
        for name in arrangement.keys():
            if (
                name in instrument.arrangements
                and scanned in instrument(instrument[name].ind_min, name).keys()
                and hasattr(arrangement[scanned], "independent")
            ):
                inds += [arrangement[scanned].independent]
    if len(inds) > 1:
        inds = np.concatenate(inds)
    else:
        inds = inds[0]

    unique = np.unique(inds)
    tol = 1e-3 * (max_ - min_)
    diff = np.append(tol * 2, np.diff(unique))
    return unique[diff > tol]


def run_holistic(detectors, opa, motor0, motor1, width, npts, spectrometer, *, md=None):
    md = md or {}
    local_md = {
        "plan_name": "run_holistic",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "opa": repr(opa),
            "motor0": motor0,
            "motor1": motor1,
            "width": width,
            "npts": npts,
            "spectrometer": _spectrometer_md(spectrometer),
        },
        "hints": {},
        "motors": [f"{opa.name}_{motor0}", f"{opa.name}_{motor1}"],
    }
    return (
        yield from motortune(
            detectors,
            opa,
            True,
            {motor1: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=local_md | md,
        )
    )


def run_intensity(detectors, opa, motor, width, npts, spectrometer, *, md=None):
    assert not spectrometer or spectrometer["method"] in ("none", "track", "zero")
    md = md or {}
    local_md = {
        "plan_name": "run_intensity",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "opa": repr(opa),
            "motor": motor,
            "width": width,
            "npts": npts,
            "spectrometer": _spectrometer_md(spectrometer),
        },
        "hints": {},
    }
    return (
        yield from motortune(
            detectors,
            opa,
            True,
            {motor: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=local_md | md,
        )
    )


def run_setpoint(detectors, opa, motor, width, npts, spectrometer, *, md=None):
    md = md or {}
    local_md = {
        "plan_name": "run_setpoint",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "opa": repr(opa),
            "motor": motor,
            "width": width,
            "npts": npts,
            "spectrometer": _spectrometer_md(spectrometer),
        },
        "hints": {},
    }
    return (
        yield from motortune(
            detectors,
            opa,
            True,
            {motor: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=local_md | md,
        )
    )


def run_tune_test(detectors, opa, spectrometer, *, md=None):
    md = md or {}
    local_md = {
        "plan_name": "run_tune_test",
        "plan_args": {
            "detectors": list(map(repr, detectors)),
            "opa": repr(opa),
            "spectrometer": _spectrometer_md(spectrometer),
        },
        "hints": {},
    }
    return (yield from motortune(detectors, opa, True, {}, spectrometer, md=local_md | md))

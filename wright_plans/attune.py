import attune
import numpy as np
from bluesky import Msg
from cycler import cycler

from ._constants import Constant, ConstantTerm
from ._messages import set_relative_to_func_wrapper, inject_set_position_except_wrapper
from ._plans import scan_nd_wp


def motortune(detectors, opa, use_tune_points, motors, spectrometer=None, *, md=None):
    cyc = 1
    md = md or {}
    instr = attune.Instrument(**opa.instrument)
    arrangement = opa.arrangement
    relative_sets = {}
    exceptions = []
    constants = {}
    axis_units = {}

    scanned_motors = [
        m for m, params in motors.items() if params.get("method") == "scan"
    ]

    if use_tune_points:
        cyc = cycler(opa, get_tune_points(instr, instr[arrangement], scanned_motors))
        axis_units[opa] = "nm"  # TODO more robust units?
    for mot, params in motors.items():
        if params["method"] == "static":
            yield Msg("set", getattr(opa, mot), params["center"])
            exceptions += [mot]
        elif params["method"] == "scan":
            exceptions += [mot]
            if use_tune_points:
                params["center"] = 0

                def _motor_rel(opa, motor):
                    def _motor_rel_inner():
                        return instr(opa.position, arrangement)[motor]

                    return _motor_rel_inner

                relative_sets[getattr(opa, mot)] = _motor_rel(opa, mot)
            cyc *= cycler(
                getattr(opa, mot),
                np.linspace(
                    params["center"] - params["width"] / 2,
                    params["center"] + params["width"] / 2,
                    params["npts"],
                ),
            )
    if spectrometer and spectrometer["device"]:
        if spectrometer["method"] == "static":
            yield Msg("set", spectrometer["device"], spectrometer["center"])
        elif spectrometer["method"] == "zero":
            yield Msg("set", spectrometer["device"], 0)
        elif spectrometer["method"] == "track":
            constants[spectrometer["device"]] = Constant("nm", [ConstantTerm(1, opa)])
        elif spectrometer["method"] == "set":
            if use_tune_points:
                constants[spectrometer["device"]] = Constant(
                    "nm", [ConstantTerm(1, opa)]
                )
            else:
                yield Msg("set", spectrometer["device"], spectrometer["center"])
        elif spectrometer["method"] == "scan":
            if use_tune_points:
                spectrometer["center"] = 0

                def _spec_rel(opa):
                    def _spec_rel_inner():
                        return opa.position

                    return _spec_rel_inner

                relative_sets[spectrometer["device"]] = _spec_rel(opa)
            cyc *= cycler(
                spectrometer["device"],
                np.linspace(
                    spectrometer["center"] - spectrometer["width"] / 2,
                    spectrometer["center"] + spectrometer["width"] / 2,
                    spectrometer["npts"],
                ),
            )
            axis_units[spectrometer["device"]] = "nm"

    plan = scan_nd_wp(detectors, cyc, axis_units=axis_units, constants=constants, md=md)
    if relative_sets:
        plan = set_relative_to_func_wrapper(plan, relative_sets)
    if exceptions:
        plan = inject_set_position_except_wrapper(plan, opa, exceptions)
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
    return (
        yield from motortune(
            detectors + [motor0],
            opa,
            True,
            {motor1: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=md,
        )
    )


def run_intensity(detectors, opa, motor, width, npts, spectrometer, *, md=None):
    assert not spectrometer or spectrometer["method"] in ("none", "track", "zero")
    return (
        yield from motortune(
            detectors,
            opa,
            True,
            {motor: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=md,
        )
    )


def run_setpoint(detectors, opa, motor, width, npts, spectrometer, *, md=None):
    return (
        yield from motortune(
            detectors,
            opa,
            True,
            {motor: {"method": "scan", "width": width, "npts": npts}},
            spectrometer,
            md=md,
        )
    )


def run_tune_test(detectors, opa, spectrometer, *, md=None):
    return (yield from motortune(detectors, opa, True, {}, spectrometer, md=md))

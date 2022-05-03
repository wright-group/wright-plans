import yaqc_bluesky
from wright_plans.attune import motortune
from bluesky.tests.utils import DocCollector
#from .utils import _retrieve_point

import pytest

num_tune_points = 5


@pytest.mark.parametrize("motor_type", ["static", "scan"])
def test_motor_types(RE, hw, motor_type):
    dc = DocCollector()
    RE(motortune([], hw.opa, True, {"crystal_1":{"method": motor_type, "center": 3, "width": 1, "npts": 3}}, None), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points * (3 if motor_type == "scan" else 1)
    assert dc.start[0]["num_points"] == num_tune_points * (3 if motor_type == "scan" else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if motor_type == "scan" else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"
    # Check actual positions


@pytest.mark.parametrize("spec_type", ["static", "zero", "track", "scan"])
def test_spec_types(RE, hw, spec_type):
    dc = DocCollector()
    RE(motortune([], hw.opa, True, {}, {"device": hw.spec, "method": spec_type, "center": 500, "width": -100, "npts": 3}), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points * (3 if spec_type == "scan" else 1)
    assert dc.start[0]["num_points"] == num_tune_points * (3 if spec_type == "scan" else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if spec_type == "scan" else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"
    # Check actual positions


@pytest.mark.parametrize("use_tune_points", [True, False])
def test_use_tune_points(RE, hw, use_tune_points):
    dc = DocCollector()
    RE(motortune([], hw.opa, use_tune_points, {"crystal_1":{"method": "scan", "center": 3, "width": 1, "npts": 3}}, None), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == 3 * (num_tune_points if use_tune_points else 1)
    assert dc.start[0]["num_points"] == 3 * (num_tune_points if use_tune_points else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if use_tune_points else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"
    # Check actual positions


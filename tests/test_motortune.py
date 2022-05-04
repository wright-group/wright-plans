import yaqc_bluesky
from wright_plans.attune import motortune
from bluesky.tests.utils import DocCollector
from .utils import _retrieve_motor_positions
import numpy as np
import numpy.testing as npt

import pytest

num_tune_points = 5


# TODO add back motor_type static tests, currently failing due to opa overriding positions
@pytest.mark.parametrize("motor_type", ["scan"])
def test_motor_types(RE, hw, motor_type):
    dc = DocCollector()
    RE(motortune([], hw.opa, True, {"crystal_1":{"method": motor_type, "center": 3, "width": 1, "npts": 3}}, None), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points * (3 if motor_type == "scan" else 1)
    assert dc.start[0]["num_points"] == num_tune_points * (3 if motor_type == "scan" else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if motor_type == "scan" else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"

    positions = _retrieve_motor_positions(dc, [hw.opa, hw.opa.crystal_1])

    if motor_type == "static":
        expected_c1 = 3
        expected_opa = np.linspace(1200, 1700, 5)
    else:
        expected_c1 = (np.stack([[-0.5, 0, 0.5]] * 5) + np.linspace(50, 100, 5)[:, None]).flatten()
        expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["w1_crystal_1"], expected_c1)



@pytest.mark.parametrize("spec_type", ["static", "zero", "track", "scan"])
def test_spec_types(RE, hw, spec_type):
    dc = DocCollector()
    RE(motortune([hw.spec], hw.opa, True, {}, {"device": hw.spec, "method": spec_type, "center": 500, "width": -100, "npts": 3}), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points * (3 if spec_type == "scan" else 1)
    assert dc.start[0]["num_points"] == num_tune_points * (3 if spec_type == "scan" else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if spec_type == "scan" else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa])

    expected_opa = np.linspace(1200, 1700, 5)
    if spec_type == "static":
        expected_spec = 500
    elif spec_type == "zero":
        expected_spec = 0
    elif spec_type == "track":
        expected_spec = positions["w1"]
    else:
        expected_spec = (np.stack([[50, 0, -50]] * 5) + np.linspace(1200, 1700, 5)[:, None]).flatten()
        expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["wm"], expected_spec)

@pytest.mark.parametrize("spec_units", ["nm", "wn"])
def test_spec_units(RE, hw, spec_units):
    dc = DocCollector()
    RE(motortune([hw.spec], hw.opa, True, {}, {"device": hw.spec, "method": "scan", "units": spec_units, "width": -100, "npts": 3}), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points * 3
    assert dc.start[0]["num_points"] == num_tune_points * 3
    assert dc.start[0]["shape"] == (num_tune_points, 3)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa])

    expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()
    if spec_units == "nm":
        expected_spec = (np.stack([[50, 0, -50]] * 5) + np.linspace(1200, 1700, 5)[:, None]).flatten()
    else:
        # Convert to wn, add, convert back to nm for comparison
        expected_spec = 1e7/(np.stack([[50, 0, -50]] * 5) + 1e7/np.linspace(1200, 1700, 5)[:, None]).flatten()

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["wm"], expected_spec)


@pytest.mark.parametrize("spec_units", ["nm", "wn"])
def test_spec_static_units(RE, hw, spec_units):
    dc = DocCollector()
    RE(motortune([hw.spec], hw.opa, True, {}, {"device": hw.spec, "method": "static", "units": spec_units, "center": 2000, "npts": 3}), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == num_tune_points
    assert dc.start[0]["num_points"] == num_tune_points
    assert dc.start[0]["shape"] == (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa])

    expected_opa = np.linspace(1200, 1700, 5)
    if spec_units == "nm":
        expected_spec = 2000
    else:
        # Convert to 2000 wn to nm for comparison
        expected_spec = 5000

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["wm"], expected_spec)




@pytest.mark.parametrize("use_tune_points", [True, False])
def test_use_tune_points(RE, hw, use_tune_points):
    dc = DocCollector()
    hw.opa.set(1300)
    RE(motortune([hw.opa], hw.opa, use_tune_points, {"crystal_1":{"method": "scan", "center": 3, "width": 1, "npts": 3}}, None), dc.insert)
    runid = list(dc.event.keys())[0]
    assert len(dc.event[runid]) == 3 * (num_tune_points if use_tune_points else 1)
    assert dc.start[0]["num_points"] == 3 * (num_tune_points if use_tune_points else 1)
    assert dc.start[0]["shape"] == (num_tune_points, 3) if use_tune_points else (num_tune_points,)
    assert dc.start[0]["plan_pattern"] == "outer_list_product"
    assert dc.start[0]["plan_name"] == "motortune"

    positions = _retrieve_motor_positions(dc, [hw.opa, hw.opa.crystal_1])

    if use_tune_points:
        expected_c1 = (np.stack([[-0.5, 0, 0.5]] * 5) + np.linspace(50, 100, 5)[:, None]).flatten()
        expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()
    else:
        expected_c1 = [2.5, 3, 3.5]
        expected_opa = 1300
    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["w1_crystal_1"], expected_c1)



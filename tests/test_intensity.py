from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_intensity
from .utils import _retrieve_motor_positions

def test_intensity(RE, hw):
    dc = DocCollector()

    RE(run_intensity([hw.daq, hw.spec], hw.opa, "crystal_1", 1, 3, spectrometer={"device": hw.spec, "method": "zero"}), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa, hw.opa.crystal_1])
    
    expected_spec = 0

    npt.assert_array_almost_equal(positions["wm"], expected_spec)

    assert dc.start[0]["plan_name"] == "run_intensity"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "w1_crystal_1"}

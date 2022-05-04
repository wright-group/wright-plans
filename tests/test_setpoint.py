from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_setpoint
from .utils import _retrieve_motor_positions

def test_setpoint(RE, hw):
    dc = DocCollector()

    RE(run_setpoint([hw.daq], hw.opa, "crystal_1", 1, 3, spectrometer={}), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.opa, hw.opa.crystal_1])
    
    expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()
    expected_c1 = (np.stack([[-0.5, 0, 0.5]] * 5) + np.linspace(50, 100, 5)[:, None]).flatten()

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["w1_crystal_1"], expected_c1)

    assert dc.start[0]["plan_name"] == "run_setpoint"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "w1_crystal_1"}

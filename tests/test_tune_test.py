from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_tune_test
from .utils import _retrieve_motor_positions

def test_tune_test(RE, hw):
    dc = DocCollector()

    RE(run_tune_test([hw.daq], hw.opa, spectrometer={"device": hw.spec, "method": "scan", "width": 100, "npts":3}), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa])
    
    expected_opa = np.stack([np.linspace(1200, 1700, 5)]*3).T.flatten()
    expected_spec = (np.stack([[-50, 0, 50]] * 5) + np.linspace(1200, 1700, 5)[:, None]).flatten()

    npt.assert_array_almost_equal(positions["w1"], expected_opa)
    npt.assert_array_almost_equal(positions["wm"], expected_spec)

    assert dc.start[0]["plan_name"] == "run_tune_test"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "wm"}

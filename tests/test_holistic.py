from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_holistic
from .utils import _retrieve_motor_positions

def test_holistic(RE, hw):

    dc = DocCollector()

    RE(run_holistic([hw.daq], hw.opa, "crystal_1", "delay_1", 1, 3, spectrometer={"device": hw.spec, "method": "track"}), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.spec, hw.opa, hw.opa.crystal_1, hw.opa.delay_1])
    
    expected_c1 = np.stack([np.linspace(50, 100, 5)]*3).T.flatten()
    expected_d1 = (np.stack([[-0.5, 0, 0.5]] * 5) + np.linspace(5, 10, 5)[:, None]).flatten()

    npt.assert_array_almost_equal(positions["wm"], positions["w1"], err_msg="Mono failed to track")
    npt.assert_array_almost_equal(positions["w1_crystal_1"], expected_c1)
    npt.assert_array_almost_equal(positions["w1_delay_1"], expected_d1)

    assert dc.start[0]["plan_name"] == "run_holistic"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1_delay_1", "w1_crystal_1"}

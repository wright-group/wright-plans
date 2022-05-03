from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import grid_scan_wp
from .utils import _retrieve_motor_positions

def test_units(RE, hw):
    dc = DocCollector()

    RE(grid_scan_wp([hw.daq], hw.d1, -1000, 1000, 3, "fs", hw.opa, 7000, 8000, 5, "wn"), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.d1, hw.opa])
    
    expected_d1 = np.stack([[-1, 0, 1]]*5).T.flatten() # in ps
    expected_opa = 1e7 / np.stack([[7000., 7250., 7500., 7750., 8000.]]*3).flatten() # in nm

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["w1"], expected_opa)

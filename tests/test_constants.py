from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import grid_scan_wp
from .utils import _retrieve_motor_positions

def test_constants(RE, hw):
    dc = DocCollector()

    RE(grid_scan_wp([hw.daq], hw.d1, -1, 1, 3, "ps", hw.d2, -1, 1, 5, "ps", constants=[[hw.d0, "ps", [[1, hw.d1],[1, hw.d2],[-1, None]]]]), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.d0, hw.d1, hw.d2])
    
    expected_d1 = np.stack([[-1, 0, 1]]*5).T.flatten()
    expected_d2 = np.stack([[-1, -0.5, 0, 0.5, 1]]*3).flatten()
    expected_d0 = expected_d1 + expected_d2 - 1

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["d2"], expected_d2)
    npt.assert_array_almost_equal(positions["d0"], expected_d0)

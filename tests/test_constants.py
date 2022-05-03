from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import grid_scan_wp
from .utils import _retrieve_motor_positions

def test_grid_scan(RE):
    d1 = yaqc_bluesky.Device(38401)
    d2 = yaqc_bluesky.Device(38402)
    d0 = yaqc_bluesky.Device(38500)
    d1.yaq_client.set_zero_position(12.5)
    d2.yaq_client.set_zero_position(12.5)
    d0.yaq_client.set_zero_position(100)
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(grid_scan_wp([sensor], d1, -1, 1, 3, "ps", d2, -1, 1, 5, "ps", constants=[[d0, "ps", [[1, d1],[1, d2],[-1, None]]]]), dc.insert)

    positions = _retrieve_motor_positions(dc, [d0, d1, d2])
    
    expected_d1 = np.stack([[-1, 0, 1]]*5).T.flatten()
    expected_d2 = np.stack([[-1, -0.5, 0, 0.5, 1]]*3).flatten()
    expected_d0 = expected_d1 + expected_d2 - 1

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["d2"], expected_d2)
    npt.assert_array_almost_equal(positions["d0"], expected_d0)

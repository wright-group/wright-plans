from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import list_grid_scan_wp
from .utils import _retrieve_motor_positions

def test_list_grid_scan(RE):
    d1 = yaqc_bluesky.Device(38401)
    d2 = yaqc_bluesky.Device(38402)
    d1.yaq_client.set_zero_position(12.5)
    d2.yaq_client.set_zero_position(12.5)
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(list_grid_scan_wp([sensor], d1, [-1, 0, 1], "ps", d2, [-1, -0.5, 0, 0.5, 1], "ps"), dc.insert)

    positions = _retrieve_motor_positions(dc, [d1, d2])
    
    expected_d1 = np.stack([[-1, 0, 1]]*5).T.flatten()
    expected_d2 = np.stack([[-1, -0.5, 0, 0.5, 1]]*3).flatten()

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["d2"], expected_d2)

    assert dc.start[0]["plan_name"] == "list_grid_scan_wp"
    assert dc.start[0]["shape"] == (3, 5)
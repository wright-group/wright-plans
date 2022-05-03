from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import grid_scan_wp
from .utils import _retrieve_motor_positions

def test_grid_scan(RE):
    d1 = yaqc_bluesky.Device(38401)
    opa = yaqc_bluesky.Device(39301)
    d1.yaq_client.set_zero_position(12.5)
    opa.yaq_client.set_arrangement("non-non-non-sig")
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(grid_scan_wp([sensor], d1, -1000, 1000, 3, "fs", opa, 7000, 8000, 5, "wn"), dc.insert)

    positions = _retrieve_motor_positions(dc, [d1, opa])
    
    expected_d1 = np.stack([[-1, 0, 1]]*5).T.flatten() # in ps
    expected_opa = 1e7 / np.stack([[7000., 7250., 7500., 7750., 8000.]]*3).flatten() 

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["w1"], expected_opa)

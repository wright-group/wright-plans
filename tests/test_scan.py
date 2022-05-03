from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans import scan_wp
from .utils import _retrieve_motor_positions

def test_scan(RE, hw):
    dc = DocCollector()

    RE(scan_wp([hw.daq], hw.d1, -1, 1, "ps", hw.d2, 1, -1, "ps", num=3), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.d1, hw.d2])
    
    expected_d1 = [-1, 0, 1]
    expected_d2 = [1, 0, -1]

    npt.assert_array_almost_equal(positions["d1"], expected_d1)
    npt.assert_array_almost_equal(positions["d2"], expected_d2)

    assert dc.start[0]["plan_name"] == "scan_wp"
    assert dc.start[0]["num_points"] == 3
    assert set(dc.start[0]["motors"]) == {"d1", "d2"}

from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_holistic
from .utils import _retrieve_motor_positions

def test_holistic(RE):
    opa = yaqc_bluesky.Device(39301)
    opa.yaq_client.set_arrangement("non-non-non-sig")
    spec = yaqc_bluesky.Device(39876)
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(run_holistic([sensor], opa, "crystal_1", "delay_1", 1, 3, spectrometer={"device": spec, "method": "track"}), dc.insert)

    positions = _retrieve_motor_positions(dc, [spec, opa, opa.crystal_1])
    
    npt.assert_array_almost_equal(positions["wm"], positions["w1"], err_msg="Mono failed to track")

    assert dc.start[0]["plan_name"] == "run_holistic"
    assert dc.start[0]["shape"] == (25, 3)
    assert set(dc.start[0]["motors"]) == {"w1_delay_1", "w1_crystal_1"}

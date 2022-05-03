from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_tune_test
from .utils import _retrieve_motor_positions

def test_tune_test(RE):
    opa = yaqc_bluesky.Device(39301)
    opa.yaq_client.set_arrangement("non-non-non-sig")
    spec = yaqc_bluesky.Device(39876)
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(run_tune_test([sensor, spec], opa, spectrometer={"device": spec, "method": "scan", "width": 100, "npts":3}), dc.insert)

    positions = _retrieve_motor_positions(dc, [spec, opa, opa.crystal_1])
    
    # TODO enforce expected positions

    assert dc.start[0]["plan_name"] == "run_tune_test"
    assert dc.start[0]["shape"] == (25, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "wm"}

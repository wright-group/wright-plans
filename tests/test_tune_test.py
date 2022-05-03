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
    
    # TODO enforce expected positions

    assert dc.start[0]["plan_name"] == "run_tune_test"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "wm"}

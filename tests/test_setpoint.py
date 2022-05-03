from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_setpoint
from .utils import _retrieve_motor_positions

def test_setpoint(RE):
    opa = yaqc_bluesky.Device(39301)
    opa.yaq_client.set_arrangement("non-non-non-sig")
    sensor = yaqc_bluesky.Device(38999)

    dc = DocCollector()

    RE(run_setpoint([sensor], opa, "crystal_1", 1, 3, spectrometer={}), dc.insert)

    positions = _retrieve_motor_positions(dc, [opa, opa.crystal_1])
    
    # TODO enforce motor positions

    assert dc.start[0]["plan_name"] == "run_setpoint"
    assert dc.start[0]["shape"] == (25, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "w1_crystal_1"}

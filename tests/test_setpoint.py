from bluesky.tests.utils import DocCollector
import yaqc_bluesky
import numpy.testing as npt
import numpy as np

from wright_plans.attune import run_setpoint
from .utils import _retrieve_motor_positions

def test_setpoint(RE, hw):
    dc = DocCollector()

    RE(run_setpoint([hw.daq], hw.opa, "crystal_1", 1, 3, spectrometer={}), dc.insert)

    positions = _retrieve_motor_positions(dc, [hw.opa, hw.opa.crystal_1])
    
    # TODO enforce motor positions

    assert dc.start[0]["plan_name"] == "run_setpoint"
    assert dc.start[0]["shape"] == (5, 3)
    assert set(dc.start[0]["motors"]) == {"w1", "w1_crystal_1"}

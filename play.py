import bluesky
import wright_plans
import yaqc_bluesky

from bluesky import plans as bsp

from bluesky.callbacks.best_effort import BestEffortCallback

from wright_plans._constants import Constant, ConstantTerm

from wright_plans.attune import motortune
from wright_plans._messages import register_set_except


from bluesky_autonomic import OPADevice

import databroker
cat = databroker.catalog["mongo"]


bec = BestEffortCallback()

d1 = yaqc_bluesky.Device(38401)
d2 = yaqc_bluesky.Device(38402)
d0 = yaqc_bluesky.Device(38500)
wm = yaqc_bluesky.Device(39876)
daq = yaqc_bluesky.Device(38999)
opa = OPADevice(yaqc_bluesky.Device(39301))

RE = bluesky.RunEngine({})
RE.subscribe(bec)
RE.subscribe(cat.v1.insert)
register_set_except(RE)

RE(motortune([daq], opa, True, {"crystal_1": {"method": "scan", "center": 0, "width": 1, "npts": 3}, "crystal_2": {"method": "static", "center": 0.1, "width": 0.3, "npts": 2}}, {"device": wm, "method": "scan", "center": 1300, "width": 500, "npts": 10}
    ))


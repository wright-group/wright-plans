import bluesky
import wright_plans
import yaqc_bluesky

from bluesky import plans as bsp

from bluesky.callbacks.best_effort import BestEffortCallback

from wright_plans._constants import Constant, ConstantTerm


bec = BestEffortCallback()

d1 = yaqc_bluesky.Device(38401)
d2 = yaqc_bluesky.Device(38402)
d0 = yaqc_bluesky.Device(38500)
wm = yaqc_bluesky.Device(39876)
daq = yaqc_bluesky.Device(38999)

RE = bluesky.RunEngine({})
RE.subscribe(bec)

md={"constants":{d2: Constant("mm", [ConstantTerm(2, d1), ConstantTerm(0.5, None)]), d0:Constant("cm", [ConstantTerm(10, d2), ConstantTerm(1, None)])}, "axis_units":{d1: "mm"}}
RE(wright_plans.grid_scan([daq], d1, 0, 10, 5, "mm",
    constants=md["constants"],
    ))


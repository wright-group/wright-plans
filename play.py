import bluesky
import wright_plans
import yaqc_bluesky

from bluesky import plans as bsp

from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()

d1 = yaqc_bluesky.Device(38401)
d2 = yaqc_bluesky.Device(38402)
d0 = yaqc_bluesky.Device(38500)
wm = yaqc_bluesky.Device(39876)
daq = yaqc_bluesky.Device(38999)

RE = bluesky.RunEngine({})
RE.subscribe(bec)

md={"constants":{"d2": ("mm", [(2, "d1"), (0.5, "")]), "d0":("cm", [(10, "d2"), (1, "")])}, "axis_units":{"d1": "mm", "wm": "wn"}}
RE(bsp.grid_scan([daq], d1, 0, 10, 5, wm, 1000, 5000, 5,
    snake_axes=True,
    md=md,
    per_step = wright_plans.make_one_nd_step(md, {"d0":d0, "d1":d1, "d2":d2, "wm": wm})))


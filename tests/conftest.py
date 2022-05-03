import pathlib
import os
import subprocess
import time
from types import SimpleNamespace

import pytest

from bluesky.tests.conftest import RE
import yaqc_bluesky


@pytest.fixture(scope="session")
def hw():
    here = pathlib.Path(__file__).parent
    os.environ["ATTUNE_STORE"] = str(here/"daemons"/"instruments")
    
    # Startup daemons
    procs = []
    for kind in ("fake_continuous_hardware", "attune", "fake_has_turret", "fake_triggered_sensor"):
        dashed = kind.replace("_", "-")
        procs.append(subprocess.Popen([f"yaqd-{dashed}", "--config", str(here/"daemons"/f"{kind}_config.toml")]))

    time.sleep(5)

    ns = SimpleNamespace()
    ns.d0 = yaqc_bluesky.Device(37670)
    ns.d1 = yaqc_bluesky.Device(37671)
    ns.d2 = yaqc_bluesky.Device(37672)
    ns.spec = yaqc_bluesky.Device(37677)
    ns.daq = yaqc_bluesky.Device(37678)
    ns.opa = yaqc_bluesky.Device(37679)

    ns.opa.yaq_client.set_arrangement("sig")
    ns.spec.yaq_client.set_turret("infrared")

    yield ns

    for proc in procs:
        proc.terminate()

    

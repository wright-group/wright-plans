__all__ = ["ureg", "get_units"]

from functools import lru_cache

import pint

ureg = pint.UnitRegistry()

ureg.define("wavenumber = 1 / cm = cm^{-1} = wn")

ureg.define("@alias s = s_t")
ureg.define("@alias min = m_t")
ureg.define("@alias hour = h_t")
ureg.define("@alias d = d_t")

ureg.define("@alias degC = deg_C")
ureg.define("@alias degF = deg_F")
ureg.define("@alias degR = deg_R")

ureg.define("@alias m = m_delay")

ureg.enable_contexts("spectroscopy")


# TODO make sure unit retrival is accurate, robust
@lru_cache
def get_units(device, default=None):
    if device is None:
        return default
    return next(iter(device.describe().values())).get("units", default)

from typing import Optional, List

from bluesky.protocols import Readable, Movable

# from pydantic import BaseModel
from dataclasses import dataclass

from ._units import ureg, get_units


@dataclass
class ConstantTerm:
    coeff: float = 0
    var: Optional[Readable] = None


@dataclass
class Constant:
    units: Optional[str]
    terms: List[ConstantTerm]

    def evaluate(self, setpoints, units: Optional[str] = None) -> float:
        quantity = ureg.Quantity(0, self.units)
        for term in self.terms:
            if term.var is None:
                quantity += ureg.Quantity(term.coeff, self.units)
                continue
            mot_units = get_units(term.var, self.units)
            # TODO: constants based on motors not scanned, some edge cases may not be possible
            # Such as the case where you want to set based on something that is moved as a result
            # of other set commands, which have not yet been told where to go
            # In that case some kind of pseudopositioner is likely the better call
            mot_quantity = ureg.Quantity(
                setpoints.get(term.var, term.var.position), mot_units
            ).to(self.units)
            mot_quantity *= term.coeff
            quantity += mot_quantity
        if units is None:
            # Use native units/cannot convert "to"
            return quantity.magnitude
        return quantity.to(units).magnitude

import bluesky
from bluesky.utils import make_decorator
from typing import List

from ._units import ureg


def inject_set_position_except_wrapper(plan, device, exceptions: List[str]):
    def _inject_set_position_except(msg):
        if msg.command == "set" and msg.obj == device:
            kwargs = msg.kwargs
            kwargs["exceptions"] = exceptions
            return bluesky.Msg("set_except", msg.obj, *msg.args, run=msg.run, **kwargs)
        return msg

    return (
        yield from bluesky.preprocessors.msg_mutator(plan, _inject_set_position_except)
    )


inject_set_position_except = make_decorator(inject_set_position_except_wrapper)


def register_set_except(RE):
    RE.register_command(
        "set_except",
        lambda msg: msg.obj.yaq_client.set_position_except(
            *msg.args, exceptions=msg.kwargs["exceptions"]
        ),
    )


def set_relative_to_func_wrapper(plan, dic):
    def _set_relative(msg):
        if msg.command == "set" and msg.obj in dic:
            args = list(msg.args)
            func = dic[msg.obj]["func"]
            native = dic[msg.obj]["native"]
            differential = dic[msg.obj]["differential"]
            quant = ureg.Quantity(func(), native).to(differential)
            quant += ureg.Quantity(args[0], differential)
            quant = quant.to(native)
            return bluesky.Msg("set", msg.obj, quant.magnitude, run=msg.run, **msg.kwargs)
        return msg

    return (yield from bluesky.preprocessors.msg_mutator(plan, _set_relative))


set_relative_to_func = make_decorator(set_relative_to_func_wrapper)

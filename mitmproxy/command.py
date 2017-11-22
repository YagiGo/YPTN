"""
    This module manges and invokes typed commands.
"""
import inspect
import typing
import shlex
import textwrap
import functools
import sys

from mitmproxy.utils import typecheck
from mitmproxy import exceptions
from mitmproxy import flow


Cuts = typing.Sequence[
    typing.Sequence[typing.Union[str, bytes]]
]


def typename(t: type, ret: bool) -> str:
    """
        Translates a type to an explanatory string. If ret is True, we're
        looking at a return type, else we're looking at a parameter type.
    """
    if issubclass(t, (str, int, bool)):
        return t.__name__
    elif t == typing.Sequence[flow.Flow]:
        return "[flow]" if ret else "flowspec"
    elif t == typing.Sequence[str]:
        return "[str]"
    elif t == Cuts:
        return "[cuts]" if ret else "cutspec"
    elif t == flow.Flow:
        return "flow"
    else:  # pragma: no cover
        raise NotImplementedError(t)


class Command:
    def __init__(self, manager, path, func) -> None:
        self.path = path
        self.manager = manager
        self.func = func
        sig = inspect.signature(self.func)
        self.help = None
        if func.__doc__:
            txt = func.__doc__.strip()
            self.help = "\n".join(textwrap.wrap(txt))

        self.has_positional = False
        for i in sig.parameters.values():
            # This is the kind for *args paramters
            if i.kind == i.VAR_POSITIONAL:
                self.has_positional = True
        self.paramtypes = [v.annotation for v in sig.parameters.values()]
        self.returntype = sig.return_annotation

    def paramnames(self) -> typing.Sequence[str]:
        v = [typename(i, False) for i in self.paramtypes]
        if self.has_positional:
            v[-1] = "*" + v[-1]
        return v

    def retname(self) -> str:
        return typename(self.returntype, True) if self.returntype else ""

    def signature_help(self) -> str:
        params = " ".join(self.paramnames())
        ret = self.retname()
        if ret:
            ret = " -> " + ret
        return "%s %s%s" % (self.path, params, ret)

    def call(self, args: typing.Sequence[str]):
        """
            Call the command with a list of arguments. At this point, all
            arguments are strings.
        """
        if not self.has_positional and (len(self.paramtypes) != len(args)):
            raise exceptions.CommandError("Usage: %s" % self.signature_help())

        remainder = []  # type: typing.Sequence[str]
        if self.has_positional:
            remainder = args[len(self.paramtypes) - 1:]
            args = args[:len(self.paramtypes) - 1]

        pargs = []
        for i in range(len(args)):
            if typecheck.check_command_type(args[i], self.paramtypes[i]):
                pargs.append(args[i])
            else:
                pargs.append(parsearg(self.manager, args[i], self.paramtypes[i]))

        if remainder:
            chk = typecheck.check_command_type(
                remainder,
                typing.Sequence[self.paramtypes[-1]]  # type: ignore
            )
            if chk:
                pargs.extend(remainder)
            else:
                raise exceptions.CommandError("Invalid value type.")

        with self.manager.master.handlecontext():
            ret = self.func(*pargs)

        if not typecheck.check_command_type(ret, self.returntype):
            raise exceptions.CommandError("Command returned unexpected data")

        return ret


class CommandManager:
    def __init__(self, master):
        self.master = master
        self.commands = {}

    def collect_commands(self, addon):
        for i in dir(addon):
            if not i.startswith("__"):
                o = getattr(addon, i)
                if hasattr(o, "command_path"):
                    self.add(o.command_path, o)

    def add(self, path: str, func: typing.Callable):
        self.commands[path] = Command(self, path, func)

    def call_args(self, path, args):
        """
            Call a command using a list of string arguments. May raise CommandError.
        """
        if path not in self.commands:
            raise exceptions.CommandError("Unknown command: %s" % path)
        return self.commands[path].call(args)

    def call(self, cmdstr: str):
        """
            Call a command using a string. May raise CommandError.
        """
        parts = shlex.split(cmdstr)
        if not len(parts) >= 1:
            raise exceptions.CommandError("Invalid command: %s" % cmdstr)
        return self.call_args(parts[0], parts[1:])

    def dump(self, out=sys.stdout) -> None:
        cmds = list(self.commands.values())
        cmds.sort(key=lambda x: x.signature_help())
        for c in cmds:
            for hl in (c.help or "").splitlines():
                print("# " + hl, file=out)
            print(c.signature_help(), file=out)
            print(file=out)


def parsearg(manager: CommandManager, spec: str, argtype: type) -> typing.Any:
    """
        Convert a string to a argument to the appropriate type.
    """
    if issubclass(argtype, str):
        return spec
    elif argtype == bool:
        if spec == "true":
            return True
        elif spec == "false":
            return False
        else:
            raise exceptions.CommandError(
                "Booleans are 'true' or 'false', got %s" % spec
            )
    elif issubclass(argtype, int):
        try:
            return int(spec)
        except ValueError as e:
            raise exceptions.CommandError("Expected an integer, got %s." % spec)
    elif argtype == typing.Sequence[flow.Flow]:
        return manager.call_args("view.resolve", [spec])
    elif argtype == Cuts:
        return manager.call_args("cut", [spec])
    elif argtype == flow.Flow:
        flows = manager.call_args("view.resolve", [spec])
        if len(flows) != 1:
            raise exceptions.CommandError(
                "Command requires one flow, specification matched %s." % len(flows)
            )
        return flows[0]
    elif argtype == typing.Sequence[str]:
        return [i.strip() for i in spec.split(",")]
    else:
        raise exceptions.CommandError("Unsupported argument type: %s" % argtype)


def command(path):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        wrapper.__dict__["command_path"] = path
        return wrapper
    return decorator

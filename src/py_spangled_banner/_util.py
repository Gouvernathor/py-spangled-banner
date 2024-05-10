from collections.abc import Callable
from inspect import signature, Parameter
import io

_file_parameter = Parameter("file",
    Parameter.POSITIONAL_OR_KEYWORD,
    annotation=str|io.TextIOBase)

def write_from_get(get_func: Callable[..., str]) -> Callable[..., None]:
    def write_func(file, *args, **kwargs):
        if isinstance(file, str):
            with open(file, "w") as f:
                return write_func(f, *args, **kwargs)
        print(get_func(*args, **kwargs), file=file)

    get_sig = signature(get_func)
    write_sig = get_sig.replace(parameters=[_file_parameter]+list(get_sig.parameters.values()))
    write_func.__signature__ = write_sig
    write_func.__name__ = get_func.__name__.replace("get_", "write_")
    return write_func

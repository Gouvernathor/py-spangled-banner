from collections.abc import Callable, Container
from inspect import signature, Parameter
import io
from typing import TypeVar

_file_parameter = Parameter("file",
    Parameter.POSITIONAL_ONLY,
    annotation=str|io.TextIOBase)

def write_from_get(get_func: Callable[..., str]) -> Callable[..., None]:
    def write_func(file, /, *args, **kwargs):
        rv = get_func(*args, **kwargs)
        if isinstance(file, str):
            with open(file, "w", encoding="UTF-8") as f:
                print(rv, file=f)
        else:
            print(rv, file=file)

    get_sig = signature(get_func)
    write_sig = get_sig.replace(
        parameters=[_file_parameter]+list(get_sig.parameters.values()),
        return_annotation=None,
    )
    write_func.__signature__ = write_sig
    write_func.__name__ = get_func.__name__.replace("get_", "write_")
    return write_func

V = TypeVar("V") # PY3.11 compat
def filter_kwargs(
        *sets: Container[str],
        **kwargs: V,
        ) -> list[dict[str, V]]:
    """
    The length of the list is one more than the number of sets passed.
    The sets may actually be any container.
    """

    rvdicts = []
    for s in sets:
        rvdict = {}
        # no set operations in order to keep the ordering
        for k in tuple(kwargs):
            if k in s:
                rvdict[k] = kwargs.pop(k)
        rvdicts.append(rvdict)

    rvdicts.append(kwargs)
    return rvdicts

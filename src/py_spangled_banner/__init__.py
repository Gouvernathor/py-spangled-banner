from inspect import signature

from ._util import filter_kwargs, write_from_get
from .stars import find_best_star_layout
from .geometry import Measurements
from .svg import get_svg_from_layout

__all__ = ("get_svg", "write_svg")

_FBSL_PARAM_NAMES = {k: p for k, p in signature(find_best_star_layout).parameters.items() if p.kind==p.KEYWORD_ONLY}
_MG_PARAM_NAMES = {k: p for k, p in signature(Measurements.generate).parameters.items() if p.kind==p.KEYWORD_ONLY and k!="star_layout"}
_GSFL_PARAM_NAMES = {k: p for k, p in signature(get_svg_from_layout).parameters.items() if p.kind==p.KEYWORD_ONLY}

def get_svg(nstars: int, **kwargs) -> str:
    fbsl_kwargs, mg_kwargs, gsfl_kwargs, kwargs = filter_kwargs(_FBSL_PARAM_NAMES, _MG_PARAM_NAMES, _GSFL_PARAM_NAMES, **kwargs)

    if kwargs:
        raise TypeError("Unknown parameters : " + ", ".join(kwargs))

    layout = find_best_star_layout(nstars, **fbsl_kwargs)
    measurements = Measurements.generate(star_layout=layout, **mg_kwargs)
    return get_svg_from_layout(measurements, layout, **gsfl_kwargs)

_sig = signature(get_svg)
get_svg.__signature__ = _sig.replace(parameters=(
    *(p for p in _sig.parameters.values() if p.kind!=p.VAR_KEYWORD),
    *_FBSL_PARAM_NAMES.values(),
    *_MG_PARAM_NAMES.values(),
    *_GSFL_PARAM_NAMES.values(),
))
del _sig

write_svg = write_from_get(get_svg)

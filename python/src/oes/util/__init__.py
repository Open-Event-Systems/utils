"""OES shared utilities library."""

from .attrs import is_attrs_class, is_attrs_instance
from .merge_dict import merge_dict

__all__ = [
    "merge_dict",
    "is_attrs_class",
    "is_attrs_instance",
    # modules
    "blacksheep",
]

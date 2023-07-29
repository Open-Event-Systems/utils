"""OES shared utilities library."""

from .attrs import is_attrs_class, is_attrs_instance
from .merge_dict import merge_dict
from .urlsafe_base64 import urlsafe_b64decode, urlsafe_b64encode

__all__ = [
    "merge_dict",
    "is_attrs_class",
    "is_attrs_instance",
    "urlsafe_b64encode",
    "urlsafe_b64decode",
    # modules
    "blacksheep",
]

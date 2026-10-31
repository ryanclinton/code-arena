"""Language plugins. Every module in this package is imported automatically,
so dropping in a new ``<language>.py`` that uses ``@register`` is all it takes."""

import importlib
import pkgutil

from .base import Language, registry

for _mod in pkgutil.iter_modules(__path__):
    if _mod.name != "base":
        importlib.import_module(f"{__name__}.{_mod.name}")


def get_language(lang_id: str) -> Language | None:
    return registry().get(lang_id)


def all_languages() -> list[Language]:
    return list(registry().values())

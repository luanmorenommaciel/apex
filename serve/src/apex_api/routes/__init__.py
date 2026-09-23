"""Router registry.

Modules in this package that expose a module-level ``router`` are mounted by
``app.create_app`` automatically. Discovery rather than a list of imports is
what lets a later task add a route file without editing ``app.py`` — and it is
the reason two units can add routes in parallel without writing to the same
file.

A module here MUST declare its own paths relative to the ``/v1`` prefix the
app applies; it must not re-declare the prefix itself.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil

from fastapi import APIRouter

log = logging.getLogger("apex_api.routes")


def discover_routers() -> list[APIRouter]:
    """Every ``router`` in this package, ordered by module name.

    Sorted so route registration is deterministic across filesystems; two
    modules that declare the same path would otherwise resolve differently
    depending on directory order.
    """
    routers: list[APIRouter] = []
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            routers.append(router)
        else:
            # Loud, because a route file whose router is missing or misnamed
            # simply would not be served, and nothing else would say so.
            log.warning(
                "apex_api.routes.%s exposes no APIRouter named 'router'; "
                "its routes are NOT served",
                info.name,
            )
    return routers

"""V2 eager ``@flow`` decorator."""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar
from functools import wraps
from typing import Any, TypeVar, overload

from rdetoolkit.core.registry import FlowSpec, register_flow

F = TypeVar("F", bound=Callable[..., Any])
_flow_stack_var: ContextVar[tuple[str, ...]] = ContextVar("rdetoolkit_flow_stack", default=())


def current_flow_id() -> str | None:
    """Return the currently executing immediate flow id, if any."""
    stack = _flow_stack_var.get()
    return stack[-1] if stack else None


def _build_flow_spec(fn: Callable[..., Any], flow_id: str | None) -> FlowSpec:
    return FlowSpec(
        id=flow_id or f"{fn.__module__}.{fn.__qualname__}",
        name=fn.__name__,
        source_location=f"{fn.__module__}:{fn.__qualname__}",
    )


@overload
def flow(func: F, /) -> F: ...


@overload
def flow(*, id: str | None = None) -> Callable[[F], F]: ...


def flow(func: F | None = None, /, *, id: str | None = None) -> F | Callable[[F], F]:  # noqa: A002
    """Decorate a plain Python function as a registered eager flow."""

    def _decorator(fn: F) -> F:
        spec = _build_flow_spec(fn, id)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            stack = _flow_stack_var.get()
            token = _flow_stack_var.set((*stack, spec.id))
            try:
                return fn(*args, **kwargs)
            finally:
                _flow_stack_var.reset(token)

        wrapper.__flow_spec__ = spec  # type: ignore[attr-defined]
        register_flow(spec, wrapper)
        return wrapper  # type: ignore[return-value]

    if func is not None:
        return _decorator(func)
    return _decorator

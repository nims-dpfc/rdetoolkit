from collections.abc import Callable
from typing import Any, TypeVar, overload

F = TypeVar("F", bound=Callable[..., Any])

def current_flow_id() -> str | None: ...

@overload
def flow(func: F, /) -> F: ...
@overload
def flow(*, id: str | None = None) -> Callable[[F], F]: ...

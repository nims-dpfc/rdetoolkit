import click
from _typeshed import Incomplete as Incomplete
from pathlib import Path
from typing import Any

logger: Incomplete

class Command(click.Command):
    def __init__(self, name: str, **attrs: Any) -> None: ...

class InitCommand:
    default_dirs: Incomplete
    def invoke(self) -> None: ...

class VersionCommand:
    def invoke(self) -> None: ...

class DockerfileGenerator:
    path: Incomplete
    def __init__(self, path: str | Path = 'Dockerfile') -> None: ...
    def generate(self) -> list[str]: ...

class RequirementsTxtGenerator:
    path: Incomplete
    def __init__(self, path: str | Path = 'requirements.txt') -> None: ...
    def generate(self) -> list[str]: ...

class InvoiceSchemaJsonGenerator:
    path: Incomplete
    def __init__(self, path: str | Path = 'invoice.schema.json') -> None: ...
    def generate(self) -> dict[str, Any]: ...

class MetadataDefJsonGenerator:
    path: Incomplete
    def __init__(self, path: str | Path = 'metadata-def.json') -> None: ...
    def generate(self) -> dict[str, Any]: ...

class InvoiceJsonGenerator:
    path: Incomplete
    def __init__(self, path: str | Path = 'invoice.json') -> None: ...
    def generate(self) -> dict[str, Any]: ...

class MainScriptGenerator:
    path: Incomplete
    def __init__(self, path: str | Path) -> None: ...
    def generate(self) -> list[str]: ...

"""Data structures for code extracted from a repository."""

from dataclasses import dataclass

@dataclass
class CodeSymbol:
    """A function, method, or class found in a source file."""

    path: str
    name: str
    kind: str
    start_line: int
    end_line: int
    source: str
    docstring: str | None = None
    parent: str | None = None   # enclosing class, e.g. "Greeter"; None for top-level

    @property
    def qualified_name(self) -> str:
        return f"{self.parent}.{self.name}" if self.parent else self.name

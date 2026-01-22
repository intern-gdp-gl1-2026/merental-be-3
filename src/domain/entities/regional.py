"""Regional domain entity with built-in validation."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Regional:
    name: str
    id: Optional[int] = None

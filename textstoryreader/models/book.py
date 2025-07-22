from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Book:
    id: str
    title: str
    file_path: str
    file_extension: str
    metadata: Dict[str, Any] = field(default_factory=dict)

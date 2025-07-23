from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ReadingState:
    book_name: str
    last_chapter_order: int = 0
    last_position_in_chapter: str
    
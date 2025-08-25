from dataclasses import dataclass


@dataclass
class ReadingState:
    book_name: str
    last_chapter_order: int = 0
    last_position_in_chapter: float = 0.0

    def to_dict(self):
        return {
            "book_name": self.book_name,
            "last_chapter_order": self.last_chapter_order,
            "last_position_in_chapter": self.last_position_in_chapter,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_name=data.get("book_name", ""),
            last_chapter_order=data.get("last_chapter_order", 0),
            last_position_in_chapter=data.get("last_position_in_chapter", 1.0),
        )

from dataclasses import dataclass


@dataclass
class ReadingState:
    book_name: str
    last_chapter_order: int = 0
    index_word_start: int = 0

    def to_dict(self):
        return {
            "book_name": self.book_name,
            "last_chapter_order": self.last_chapter_order,
            "index_word_start": self.index_word_start,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_name=data.get("book_name", ""),
            last_chapter_order=data.get("last_chapter_order", 0),
            index_word_start=data.get("index_word_start", 0),
        )

from dataclasses import dataclass


@dataclass
class Book:
    book_name: str
    book_title: str
    file_path: str
    file_extension: str

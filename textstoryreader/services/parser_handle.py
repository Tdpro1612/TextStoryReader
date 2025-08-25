from textstoryreader.models.book import Book
from textstoryreader.services.parsers.factory_parser import ParserFactory


class ParserHandle:
    def __init__(self, book: Book):
        self.book = book
        self.parser = ParserFactory().get_parser(self.book)

    def parse(self):
        return self.parser.parse(self.book.file_path)

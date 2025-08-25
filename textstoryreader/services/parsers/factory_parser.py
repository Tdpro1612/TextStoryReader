from textstoryreader.models.book import Book

# from textstoryreader.services.parsers.parser_epub import EpubParser
from textstoryreader.services.parsers.parser_html import ParserHtml
from textstoryreader.services.parsers.parser_txt import ParserTxt
from textstoryreader.ui.utils import show_error_popup


class ParserFactory:
    def get_parser(self, book: Book):
        print(f"Debug file extension is {book.file_extension}")
        if book.file_extension == ".txt":
            return ParserTxt()
        # elif book.extension == 'epub':
        #     return EpubParser()
        if book.file_extension == ".html":
            return ParserHtml()
        # Thêm các trường hợp khác
        show_error_popup("Lỗi định dạng", f"Định dạng file không được hỗ trợ: {book.file_extension}")
        return None

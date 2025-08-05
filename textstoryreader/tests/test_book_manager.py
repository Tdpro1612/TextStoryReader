from textstoryreader.managers.book_manager import BookManager


def test_get_book_list():
    manager = BookManager()
    book_list = manager.get_book_list()
    print(f"Test result: {book_list}")

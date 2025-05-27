import os

BOOK_FOLDER = 'books'

def read_book_txt(filename):
    """
    Đọc nội dung của file .txt từ thư mục 'books' dựa trên tên file đầy đủ.
    """
    filepath = os.path.join(BOOK_FOLDER, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file sách '{filepath}'")
        return None
    except Exception as e:
        print(f"Lỗi đọc file '{filepath}': {e}")
        return None

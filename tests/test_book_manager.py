import os
import sys
from managers.book_manager import BookManager


# Lấy đường dẫn tuyệt đối của thư mục chứa script test này
current_dir = os.path.dirname(os.path.abspath(__file__))

# Lấy đường dẫn tuyệt đối của thư mục gốc của dự án (cấp trên của thư mục 'managers')
# Giả sử cấu trúc của bạn là:
# project_root/
# ├── managers/
# │   └── book_manager.py
# └── tests/
#     └── test_book_manager.py (file test của bạn)
#
# Khi đó, bạn cần thêm 'project_root' vào sys.path.
# 'current_dir' là 'project_root/tests'
# 'os.path.dirname(current_dir)' sẽ là 'project_root'
project_root = os.path.dirname(current_dir)

# Thêm đường dẫn gốc của dự án vào sys.path
# Việc này đảm bảo Python có thể tìm thấy 'managers' như một package
sys.path.insert(
    0, project_root
)  # sys.path.insert(0, ...) ưu tiên tìm kiếm ở đường dẫn này trước


def test_get_book_list():
    # Khởi tạo BookManager bên trong hàm test nếu bạn không dùng fixture
    # Hoặc truyền nó qua fixture nếu có nhiều test
    book_manager = BookManager()

    # Thực hiện hành động cần kiểm tra
    books = book_manager.get_book_list()

    # Đặt các câu lệnh ASSERT để kiểm tra kết quả
    assert isinstance(books, list)  # Ví dụ: đảm bảo kết quả là một list
    # assert len(books) >= 0 # Ví dụ: đảm bảo list không âm
    print(f"DEBUG: Danh sách sách tìm thấy: {books}")

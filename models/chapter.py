# models/chapter.py


class Chapter:
    """
    Đại diện cho một chương trong nội dung của sách, đã được xử lý và chia thành các trang.
    """

    def __init__(self, title: str):
        """
        Khởi tạo một đối tượng Chapter.

        Args:
            title (str): Tiêu đề của chương (ví dụ: "Chương 1: Bắt đầu cuộc phiêu lưu").
        """
        self.title = title
        self.pages: list[
            str
        ] = []  # Danh sách các chuỗi nội dung của từng trang sau khi đã phân tách

    def add_page(self, page_content: str):
        """
        Thêm một chuỗi nội dung trang vào danh sách các trang của chương này.

        Args:
            page_content (str): Nội dung của một trang (đã được phân trang).
        """
        self.pages.append(page_content)

    def get_page_count(self) -> int:
        """
        Trả về tổng số trang trong chương này.
        """
        return len(self.pages)

    def get_page_content(self, page_index: int) -> str | None:
        """
        Trả về nội dung của một trang cụ thể trong chương.

        Args:
            page_index (int): Chỉ mục của trang cần lấy (bắt đầu từ 0).

        Returns:
            str | None: Nội dung của trang hoặc None nếu chỉ mục không hợp lệ.
        """
        if 0 <= page_index < len(self.pages):
            return self.pages[page_index]
        return None

    def __repr__(self):
        """
        Trả về biểu diễn chuỗi của đối tượng Chapter, hữu ích cho việc debug.
        """
        return f"Chapter(title='{self.title}', pages={len(self.pages)})"

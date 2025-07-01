class Book:
    

    def __init__(self, filename: str, title: str, filepath: str, file_type: str):
        """
        Args:
            filename (str): Tên file của sách (ví dụ: "simple_story.txt").
            title (str): Tiêu đề hiển thị của sách (ví dụ: "Simple Story").
            filepath (str): Đường dẫn đầy đủ đến file sách trên hệ thống. books/simple_story_html.html
            file_type (str): Loại file của sách (ví dụ: "txt" hoặc "html").
        """
        self.filename = filename
        self.title = title
        self.filepath = filepath
        self.file_type = file_type

    def __repr__(self):
        """
        Trả về biểu diễn chuỗi của đối tượng Book, hữu ích cho việc debug.
        """
        return f"Book(title='{self.title}', filename='{self.filename}', type='{self.file_type}')"

    def __eq__(self, other):
        """
        Kiểm tra xem hai đối tượng Book có bằng nhau không dựa trên filepath.
        Điều này quan trọng khi so sánh sách (ví dụ: trong danh sách).
        """
        if not isinstance(other, Book):
            return NotImplemented
        return self.filepath == other.filepath

    def __hash__(self):
        """
        Trả về giá trị hash của đối tượng Book, cho phép sử dụng trong set hoặc dict keys.
        """
        return hash(self.filepath)
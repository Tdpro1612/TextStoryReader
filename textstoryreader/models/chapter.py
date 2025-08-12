from dataclasses import dataclass


@dataclass
class Chapter:
    """
    Biểu diễn một chương của sách.
    """

    order: int  # Thứ tự của chương (bắt đầu từ 0 hoặc 1)
    title: str  # Tiêu đề của chương
    content: str

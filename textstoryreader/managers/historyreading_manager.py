import json
import os
from typing import Dict

from textstoryreader.models.readingstate import ReadingState


class HistoryReadingManager:
    def __init__(self, json_path="textstoryreader/data/history.json"):
        self.history: Dict[str, ReadingState] = {}
        self.json_path = json_path
        self.ensure_path_exists()
        self.load_history()

    def ensure_path_exists(self):
        """
        Đảm bảo thư mục chứa tệp tin JSON tồn tại.
        Nếu không, sẽ tạo thư mục và tệp tin rỗng.
        """
        # Lấy đường dẫn của thư mục
        directory = os.path.dirname(self.json_path)

        # Kiểm tra nếu thư mục không tồn tại
        if not os.path.exists(directory):
            print(f"Thư mục '{directory}' không tồn tại, đang tạo...")
            os.makedirs(directory)
            print("Đã tạo thư mục thành công.")

        # Kiểm tra nếu tệp tin không tồn tại
        if not os.path.exists(self.json_path):
            print(f"Tệp tin '{self.json_path}' không tồn tại, đang tạo tệp rỗng...")
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)  # Ghi một đối tượng JSON rỗng vào tệp
            print("Đã tạo tệp thành công.")

    def save_history(self, book_name: str, last_chapter_order: int, last_position_in_chapter: float):
        print(f"DEBUG (ReadingHistoryManager): Saved history last_chapter_order for {last_chapter_order}")
        self.history[book_name] = ReadingState(
            book_name=book_name, last_chapter_order=last_chapter_order, last_position_in_chapter=last_position_in_chapter
        )
        print(f"DEBUG (ReadingHistoryManager): Saved history for {book_name}")
        self.save_to_file()

    def get_all_history(self):
        return self.history

    def get_history(self, book_name: str) -> ReadingState:
        return self.history.get(book_name, ReadingState(book_name=book_name))

    def clear_history(self) -> None:
        self.history.clear()
        self.save_to_file()

    def save_to_file(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                # Convert all ReadingState objects to dict before dumping
                json.dump({k: v.to_dict() for k, v in self.history.items()}, f, ensure_ascii=False, indent=2)
            print(f"DEBUG (ReadingHistoryManager): History saved to {self.json_path}")
        except Exception as e:
            print(f"ERROR (ReadingHistoryManager): Cannot save history to {self.json_path}: {e}")

    def load_history(self):
        if not os.path.exists(self.json_path):
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = {k: ReadingState.from_dict(v) for k, v in data.items()}
            print(f"DEBUG (ReadingHistoryManager): Loaded history from {self.json_path}")
        except Exception as e:
            print(f"ERROR (ReadingHistoryManager): Cannot load history from {self.json_path}: {e}")

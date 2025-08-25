import os

from textstoryreader.services.parsers.parser_base import BaseParser


class ParserTxt(BaseParser):
    def parse(self, full_filepath: str):
        """
        Args:
            full_filepath (str): Đường dẫn đầy đủ tới file .txt.

        Returns:
            tuple: (content_list, chapter_title_list)
                   - content_list: Danh sách chuỗi nội dung của từng chương.
                   - chapter_title_list: Danh sách chuỗi tiêu đề của từng chương.
                   Trả về ([], []) nếu có lỗi.
        """
        try:
            with open(full_filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            title = os.path.splitext(os.path.basename(full_filepath))[0].replace("_", " ").title()

            content_list = [content]
            chapter_title_list = [title]

            return content_list, chapter_title_list

        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file tại đường dẫn: {full_filepath}")
            return [], []
        except Exception as e:
            print(f"Lỗi khi đọc file TXT: {e}")
            return [], []

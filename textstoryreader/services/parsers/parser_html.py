import os

from bs4 import BeautifulSoup, NavigableString, Tag

from textstoryreader.services.parsers.parser_base import BaseParser


class ParserHtml(BaseParser):
    def parse(self, full_filepath: str):
        """
        Phân tích cú pháp HTML và trích xuất nội dung cùng tiêu đề chương.

        Args:
            full_filepath (str): Đường dẫn đầy đủ tới file HTML.

        Returns:
            tuple: (content_list, chapter_title_list)
                   - content_list: Danh sách chuỗi nội dung của từng chương.
                   - chapter_title_list: Danh sách chuỗi tiêu đề của từng chương.
                   Trả về ([], []) nếu có lỗi.
        """
        content_list = []
        chapter_title_list = []

        try:
            with open(full_filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            body_tag = soup.find("body")
            if not body_tag:
                return [], []

            # Xóa các thành phần không phải nội dung (ví dụ: mục lục)
            toc_div = body_tag.find("div", id="table-of-contents")
            if toc_div:
                toc_div.extract()

            current_chapter_content = ""
            current_chapter_title = ""
            main_heading_tags = ["h1", "h2"]
            is_first_chapter = True

            for element in body_tag.children:
                if isinstance(element, NavigableString) and not str(element).strip():
                    continue

                if element.name in main_heading_tags and isinstance(element, Tag):
                    if not is_first_chapter:
                        # Lưu chương trước đó
                        content_list.append(current_chapter_content.strip())
                        chapter_title_list.append(current_chapter_title)

                    # Bắt đầu chương mới
                    current_chapter_title = element.get_text(strip=True)
                    current_chapter_content = ""
                    is_first_chapter = False

                # Thêm nội dung vào chương hiện tại (kể cả thẻ tiêu đề)
                if isinstance(element, Tag):
                    current_chapter_content += element.get_text(strip=True) + "\n\n"
                elif isinstance(element, NavigableString):
                    current_chapter_content += str(element).strip() + " "

            # Lưu chương cuối cùng sau khi vòng lặp kết thúc
            if current_chapter_content:
                content_list.append(current_chapter_content.strip())
                if is_first_chapter:  # Xử lý trường hợp chỉ có 1 chương
                    chapter_title_list.append(os.path.basename(full_filepath))
                else:
                    chapter_title_list.append(current_chapter_title)

            # Trường hợp file rỗng
            if not content_list:
                return [], []

            return content_list, chapter_title_list

        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file tại đường dẫn: {full_filepath}")
            return [], []
        except Exception as e:
            print(f"Lỗi khi đọc hoặc parse file HTML: {e}")
            return [], []


# Ví dụ sử dụng:
# if __name__ == "__main__":
#     file_path = "textstoryreader/books/simple_story_for_app.html"
#     parser = ParserHtml()
#     content, chapters = parser.parse(file_path)

#     print("Nội dung:", content)
#     print("Tiêu đề chương:", chapters)
#     print(f"Độ dài của nội dung: {len(content)}")
#     print(f"Độ dài của tiêu đề: {len(chapters)}")

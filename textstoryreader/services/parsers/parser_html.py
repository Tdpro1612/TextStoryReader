import os

from bs4 import BeautifulSoup, NavigableString, Tag

from textstoryreader.services.parsers.parser_base import BaseParser


class ParserHtml(BaseParser):
    def parse(self, full_filepath: str):
        content_list = []
        chapter_title_list = []

        try:
            with open(full_filepath, "r", encoding="utf-8") as f:
                # *** Tối ưu #1: Dùng "lxml" nếu có để parse nhanh hơn ***
                # Thay "html.parser" bằng "lxml" nếu bạn đã cài đặt thư viện lxml.
                soup = BeautifulSoup(f.read(), "html.parser")

            body_tag = soup.find("body")
            if not body_tag:
                return [], []

            # Xóa các thành phần không phải nội dung (ví dụ: mục lục)
            # Dòng này đã được tối ưu: Chỉ cần tìm và extract là được
            toc_div = body_tag.find("div", id="table-of-contents")
            if toc_div:
                toc_div.extract()

            # *** Tối ưu #2: Dùng danh sách để thu thập nội dung ***
            current_chapter_contents = []  # Danh sách chuỗi, hiệu quả hơn khi nối
            current_chapter_title = ""
            main_heading_tags = ["h1", "h2"]
            is_first_chapter = True

            # Duyệt qua các phần tử con
            for element in body_tag.children:
                # Bỏ qua khoảng trắng và chuỗi rỗng
                if isinstance(element, NavigableString) and not str(element).strip():
                    continue

                is_heading = element.name in main_heading_tags and isinstance(element, Tag)

                if is_heading:
                    if not is_first_chapter:
                        # Lưu chương trước đó
                        # Nối chuỗi MỘT LẦN DUY NHẤT bằng .join()
                        content_list.append("".join(current_chapter_contents).strip())
                        chapter_title_list.append(current_chapter_title)

                    # Bắt đầu chương mới
                    current_chapter_title = element.get_text(strip=True)
                    current_chapter_contents = []  # Reset danh sách nội dung cho chương mới
                    is_first_chapter = False

                    # RẤT QUAN TRỌNG: Bỏ qua việc xử lý nội dung cho thẻ tiêu đề
                    # để tránh thêm tiêu đề vào nội dung chương.
                    continue

                # Thêm Nội dung vào danh sách
                if isinstance(element, Tag):
                    text = element.get_text(strip=True)
                    if text:
                        # Thu thập chuỗi, dùng "\n\n" để phân tách đoạn văn
                        current_chapter_contents.append(text + "\n\n")
                elif isinstance(element, NavigableString):
                    text = str(element).strip()
                    if text:
                        # Thu thập chuỗi, dùng " " để phân tách chuỗi nằm ngoài thẻ
                        current_chapter_contents.append(text + " ")

            # Lưu chương cuối cùng sau khi vòng lặp kết thúc
            if current_chapter_contents:
                # Nối chuỗi cuối cùng
                content_list.append("".join(current_chapter_contents).strip())
                if is_first_chapter:
                    chapter_title_list.append(os.path.basename(full_filepath))
                else:
                    chapter_title_list.append(current_chapter_title)

            return content_list, chapter_title_list

        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file tại đường dẫn: {full_filepath}")
            return [], []
        except Exception as e:
            print(f"Lỗi khi đọc hoặc parse file HTML: {e}")
            return [], []

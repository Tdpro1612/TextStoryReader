import os

from bs4 import BeautifulSoup, NavigableString, Tag

from textstoryreader.services.parsers.parser_base import BaseParser

# Đã yêu cầu cài đặt lxml
HTML_PARSER = "lxml"

class ParserHtml(BaseParser):
    """
    Phân tích cú pháp tệp HTML để trích xuất tiêu đề và nội dung các chương.
    Các chương được phân tách bởi các thẻ tiêu đề (mặc định là <h1>, <h2>).
    """

    def parse(self, full_filepath: str):
        content_list = []
        chapter_title_list = []
        parsing_root = None 

        try:
            with open(full_filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), HTML_PARSER)

            if not soup.contents:
                 print(f"DEBUG: File is empty or could not be parsed.")
                 return [], []
            
            # Khắc phục lỗi: Xử lý linh hoạt khi thiếu <body> tag
            body_tag = soup.find("body")
            parsing_root = body_tag if body_tag else soup 
            
            # -----------------
            # *** CẢI TIẾN #1: LOẠI BỎ CÁC THẺ CÓ CLASS ***
            # Loại bỏ các thẻ có thuộc tính 'class' để lọc quảng cáo, footer, boilerplate.
            # Trừ các thẻ tiêu đề (h1, h2, h3) ra để giữ lại tiêu đề chương.
            main_heading_tags = {"h1", "h2", "h3"} 
            
            elements_to_remove = []
            for element in parsing_root.find_all(True): # Tìm TẤT CẢ các thẻ
                # Nếu thẻ có thuộc tính 'class' và KHÔNG phải là thẻ tiêu đề, thì đánh dấu để xóa.
                if element.attrs.get('class') and element.name not in main_heading_tags:
                    # Rất quan trọng: Chỉ đánh dấu để xóa, không xóa ngay khi đang duyệt.
                    elements_to_remove.append(element)
            
            for element in elements_to_remove:
                try:
                    element.extract()
                except Exception:
                    # Bỏ qua nếu thẻ đã bị extract bởi một thẻ cha đã bị extract trước đó
                    pass 

            # Xóa mục lục (sau khi đã loại bỏ các thẻ có class)
            toc_div = parsing_root.find("div", id="table-of-contents")
            if toc_div:
                toc_div.extract()

            # Thiết lập biến cho quá trình phân tích
            current_chapter_contents = [] 
            current_chapter_title = ""
            is_first_chapter = True

            # -----------------
            # CẢI TIẾN #2: Duyệt qua TẤT CẢ nội dung con của parsing_root
            # -----------------
            for element in parsing_root.contents: 
                # Bỏ qua khoảng trắng và chuỗi rỗng
                if isinstance(element, NavigableString) and not str(element).strip():
                    continue

                # LOGIC PHÂN CHIA CHƯƠNG
                is_heading = isinstance(element, Tag) and element.name in main_heading_tags

                if is_heading:
                    # 1. Lưu chương trước đó
                    if not is_first_chapter:
                        content = "".join(current_chapter_contents).strip()
                        if content: 
                            content_list.append(content)
                            chapter_title_list.append(current_chapter_title)
                    
                    # 2. Bắt đầu chương mới
                    current_chapter_title = element.get_text(strip=True)
                    current_chapter_contents = [] 
                    is_first_chapter = False

                    continue 

                # LOGIC THÊM NỘI DUNG
                if isinstance(element, Tag):
                    # Sử dụng get_text(separator=' ') để nội dung trong thẻ Tag không bị dính vào nhau.
                    text = element.get_text(separator=' ', strip=True) 
                    if text:
                        # Thêm '\n\n' để phân tách đoạn văn/thẻ, làm cho nội dung dễ đọc hơn
                        current_chapter_contents.append(text + "\n\n")
                elif isinstance(element, NavigableString):
                    # Xử lý text node nằm ngoài thẻ
                    text = str(element).strip()
                    if text:
                        current_chapter_contents.append(text + " ")


            # LƯU CHƯƠNG CUỐI CÙNG
            if current_chapter_contents:
                content = "".join(current_chapter_contents).strip()
                if content:
                    content_list.append(content)
                    
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
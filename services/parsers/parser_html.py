import json
import os
import re

from bs4 import BeautifulSoup, NavigableString, Tag

BOOK_FOLDER = "books"


def read_book_html(full_filepath):
    """
    Đọc nội dung của file HTML từ thư mục 'books' và chuyển đổi nó thành
    một danh sách chapter theo form chuẩn (index, title, content).
    Nội dung chapter sẽ là văn bản thuần túy (plain text), không còn HTML tags.

    Args:
        filename (str): Tên file HTML (ví dụ: 'my_story.html').

    Returns:
        tuple: (book_data, chapter_list_for_chapter_screen)
               - book_data: Danh sách các từ điển chapter theo form chuẩn:
                            [{'index': 0, 'title': '...', 'content': '...'}, ...]
               - chapter_list_for_chapter_screen: Danh sách đơn giản chỉ gồm index và title cho ChapterScreen.
               Trả về ([], []) nếu có lỗi hoặc không đọc được file.
    """

    try:
        with open(full_filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        filename = (
            os.path.splitext(os.path.basename(full_filepath))[0]
            .replace("_", " ")
            .title()
        )
        soup = BeautifulSoup(html_content, "html.parser")

        book_data = []  # Đây là list chứa dữ liệu theo form chuẩn: index, title, content (plain text)
        chapter_list_for_chapter_screen = []  # Danh sách đơn giản cho ChapterScreen

        body_tag = soup.find("body")
        if not body_tag:
            print(
                f"CẢNH BÁO (read_book_html): Không tìm thấy thẻ <body> trong file '{filename}'."
            )
            book_data.append(
                {
                    "index": 0,
                    "title": "Không có nội dung",
                    "content": "Không có nội dung sách để hiển thị.",
                }
            )
            chapter_list_for_chapter_screen.append(
                {"index": 0, "title": "Không có nội dung"}
            )
            return book_data, chapter_list_for_chapter_screen

        # --- Bước 1: Xóa các phần không phải nội dung (ví dụ: Mục lục) ---
        # Tìm và xóa thẻ div có id="table-of-contents" để nó không bị coi là nội dung chương
        toc_div = body_tag.find("div", id="table-of-contents")
        if toc_div:
            toc_div.extract()  # .extract() sẽ xóa thẻ khỏi cây Beautiful Soup

        # --- Bước 2: Duyệt qua các thẻ con của body và gom nhóm nội dung thành chương ---
        current_chapter_elements = []  # Lưu trữ các thẻ (hoặc chuỗi) của chương hiện tại
        current_chapter_title_text = (
            os.path.splitext(filename)[0].replace("_", " ").title()
        )  # Tiêu đề mặc định cho chương đầu tiên/giới thiệu
        chapter_counter = 0

        # Chúng ta sẽ coi h1 và h2 là các điểm bắt đầu chương chính
        # h3, h4, h5, h6 sẽ được coi là nội dung của chương hiện tại
        main_heading_tags = ["h1", "h2"]

        # Biến cờ để biết liệu chúng ta đã tìm thấy chương chính đầu tiên chưa
        found_first_main_chapter = False

        for element in body_tag.children:
            # Bỏ qua các NavigableString chỉ chứa khoảng trắng
            if isinstance(element, NavigableString) and not str(element).strip():
                continue

            # Nếu là một thẻ tiêu đề chính (h1, h2)
            if element.name in main_heading_tags and isinstance(element, Tag):
                # Nếu đã có nội dung được gom nhóm cho chương trước đó, lưu nó lại
                if current_chapter_elements:
                    # Nối các phần tử và chuyển thành văn bản thuần túy
                    chapter_content_soup = BeautifulSoup("", "html.parser")
                    for el in current_chapter_elements:
                        chapter_content_soup.append(el)
                    plain_text_content = chapter_content_soup.get_text(
                        separator="\n\n", strip=True
                    )

                    book_data.append(
                        {
                            "index": chapter_counter,
                            "title": current_chapter_title_text,
                            "content": plain_text_content,
                        }
                    )
                    chapter_list_for_chapter_screen.append(
                        {"index": chapter_counter, "title": current_chapter_title_text}
                    )
                    chapter_counter += 1

                # Bắt đầu chương mới
                current_chapter_title_text = element.get_text(strip=True)
                if not current_chapter_title_text:
                    current_chapter_title_text = f"Chương tự động {chapter_counter + 1}"

                current_chapter_elements = [
                    element
                ]  # Thêm thẻ tiêu đề vào nội dung chương mới
                found_first_main_chapter = True  # Đã tìm thấy chương chính đầu tiên
            else:  # Nếu không phải thẻ tiêu đề chính (là p, div, h3-h6, hoặc NavigableString có nội dung)
                current_chapter_elements.append(element)

        # Lưu chương cuối cùng sau khi vòng lặp kết thúc
        if current_chapter_elements:
            chapter_content_soup = BeautifulSoup("", "html.parser")
            for el in current_chapter_elements:
                chapter_content_soup.append(el)
            plain_text_content = chapter_content_soup.get_text(
                separator=" ", strip=True
            )

            # Nếu không tìm thấy chương chính nào, thì chương đầu tiên (mà là phần giới thiệu) sẽ là index 0
            # Ngược lại, nếu đã có chương chính, thì nó sẽ là chapter_counter hiện tại
            final_chapter_index = chapter_counter if found_first_main_chapter else 0
            final_chapter_title = current_chapter_title_text

            # Xử lý trường hợp đặc biệt: nếu chỉ có nội dung giới thiệu mà không có h1/h2 nào
            # hoặc nếu tiêu đề cuối cùng vẫn là tiêu đề mặc định và có nội dung
            if not found_first_main_chapter and not book_data and plain_text_content:
                final_chapter_title = (
                    os.path.splitext(filename)[0].replace("_", " ").title()
                )
                final_chapter_index = 0

            book_data.append(
                {
                    "index": final_chapter_index,
                    "title": final_chapter_title,
                    "content": plain_text_content,
                }
            )
            chapter_list_for_chapter_screen.append(
                {"index": final_chapter_index, "title": final_chapter_title}
            )

        # --- Fallback: Nếu book_data vẫn rỗng sau khi xử lý (ví dụ: file chỉ có HTML trống rỗng) ---
        if not book_data:
            book_data.append(
                {
                    "index": 0,
                    "title": "Không có nội dung",
                    "content": "Không có nội dung sách để hiển thị.",
                }
            )
            chapter_list_for_chapter_screen.append(
                {"index": 0, "title": "Không có nội dung"}
            )
            print(
                f"DEBUG (read_book_html): File HTML rỗng hoặc không có nội dung hợp lệ."
            )

        print(
            f"DEBUG (read_book_html): Đã parse '{filename}' thành {len(book_data)} chương."
        )
        return book_data, chapter_list_for_chapter_screen

    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file sách '{filepath}'")
        return [], []
    except Exception as e:
        print(f"LỖI đọc hoặc parse file HTML '{filepath}': {e}")
        return [], []


# if __name__ == "__main__":
#     # Đảm bảo thư mục 'books' tồn tại và có file test
#     bookdata, _ = read_book_html("simple_story_html.html")
#     with open("new.json", "w", encoding="utf-8") as file:
#         json.dump(bookdata, file, ensure_ascii=False, indent=4)

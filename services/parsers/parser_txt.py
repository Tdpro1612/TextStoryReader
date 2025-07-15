import os
import json

# BOOK_FOLDER không còn là hằng số toàn cục nữa,
# mà đường dẫn đến thư mục sách sẽ được quản lý bởi BookManager (hoặc nơi gọi hàm này)

def read_book_txt(full_filepath): # Đổi tên tham số để rõ ràng hơn
    """
    Đọc nội dung của file .txt từ một đường dẫn đầy đủ đã cho và chuyển đổi nó thành
    một danh sách chapter theo form chuẩn.

    Hiện tại, toàn bộ file sẽ được coi là một chương duy nhất.

    Args:
        full_filepath (str): Đường dẫn tuyệt đối đến file .txt (ví dụ: '/storage/emulated/0/Documents/TextStoryReader/books/my_story.txt').

    Returns:
        tuple: (list_of_chapters, chapter_list_for_chapter_screen)
               - list_of_chapters: Danh sách các từ điển chapter theo form chuẩn.
               - chapter_list_for_chapter_screen: Danh sách đơn giản chỉ gồm title và link/id cho ChapterScreen.
               Trả về ([], []) nếu có lỗi hoặc không đọc được file.
    """
    print(f"DEBUG (read_book_txt): Sách TXT đang được đọc từ '{full_filepath}'.")

    try:
        with open(full_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Lấy tên file từ đường dẫn đầy đủ để làm tiêu đề
        title = os.path.splitext(os.path.basename(full_filepath))[0].replace('_', ' ').title()

        book_data = [
            {
                'title': title,
                'index': 0, # Vẫn là một chương duy nhất
                'content': content.strip()
            }
        ]

        # Tạo danh sách chapter đơn giản cho ChapterScreen
        chapter_list_for_chapter_screen = [
            {'title': chapter['title'], 'link': chapter['index']}
            for chapter in book_data
        ]

        return book_data, chapter_list_for_chapter_screen

    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file sách '{full_filepath}'")
        return [], []
    except Exception as e:
        print(f"LỖI đọc file TXT '{full_filepath}': {e}")
        return [], []

# Hàm này không cần thay đổi gì, vì nó chỉ là logic chia chương
def auto_split_chapter(text):
    pass
import re

from kivy.metrics import (
    dp,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def show_error_popup(title, message):
    content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
    content.add_widget(
        Label(
            text=message,
            halign="center",
            valign="middle",
            text_size=(dp(250), None),
        )
    )

    close_button = Button(text="Đóng", size_hint=(1, None), height=dp(40))
    content.add_widget(close_button)

    popup = Popup(
        title=title,
        content=content,
        size_hint=(None, None),
        size=(dp(300), dp(200)),
        auto_dismiss=False,
    )

    close_button.bind(on_release=popup.dismiss)
    popup.open()


def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        rgb = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    elif len(hex_color) == 3:
        rgb = [int(hex_color[i] * 2, 16) / 255.0 for i in range(3)]
    else:
        rgb = [0, 0, 0]
    return rgb + [1.0]


def rgba_to_hex_6(rgba_color: list) -> str:
    """
    Chuyển đổi danh sách màu RGBA (0.0-1.0) thành chuỗi HEX 6 chữ số (#RRGGBB).

    Args:
        rgba_color: Danh sách chứa 4 giá trị float RGBA.

    Returns:
        Chuỗi HEX đã được định dạng.
    """
    # Lấy 3 giá trị đầu tiên (RGB) và bỏ qua alpha
    r, g, b = rgba_color[0], rgba_color[1], rgba_color[2]

    # Chuyển đổi các giá trị float (0.0-1.0) sang int (0-255)
    # và định dạng thành chuỗi hex 2 chữ số
    r_hex = f"{int(r * 255):02x}"
    g_hex = f"{int(g * 255):02x}"
    b_hex = f"{int(b * 255):02x}"

    return f"#{r_hex}{g_hex}{b_hex}"


def token_text_string_to_word(text):
    """
    Chia một chuỗi văn bản thành một danh sách các từ theo các quy tắc sau:
    - Chia tại dấu cách.
    - Dấu xuống dòng ('\\n') được xem là một từ riêng biệt.
    - Dấu câu ('!', '?', '.') được giữ lại và nối vào từ liền kề, nhưng sẽ tách từ nếu không có dấu cách.
      Ví dụ: "học.Tôi" sẽ được tách thành "học." và "Tôi".

    Tham số:
    text (str): Chuỗi văn bản đầu vào.

    Trả về:
    list: Danh sách các từ đã được chia.
    """
    # Bước 1: Thêm dấu cách sau các dấu câu nếu chúng đứng trước một chữ cái.
    # Điều này giải quyết trường hợp "học.Tôi" thành "học. Tôi".
    # Biểu thức chính quy: tìm một trong các ký tự .?! theo sau bởi một chữ cái.
    # Thay thế bằng chính ký tự đó, thêm một dấu cách và giữ lại chữ cái.
    text_with_spaces = re.sub(r"([.?!])([a-zA-Záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ])", r"\1 \2", text)

    # Bước 2: Thay thế dấu xuống dòng ('\\n') bằng một token đặc biệt để nó được coi là một từ.
    temp_text = text_with_spaces.replace("\n", " <NEWLINE> ")

    # Bước 3: Chia chuỗi thành các từ dựa trên khoảng trắng.
    words = temp_text.split()

    # Bước 4: Thay thế token đặc biệt trở lại thành dấu xuống dòng.
    words_tokens = ["\n" if word == "<NEWLINE>" else word for word in words]

    return words_tokens


def text_slicer_forward(word_list, index_start, max_lines, max_chars_per_line):
    """
    Sắp xếp các từ từ một danh sách vào các dòng dựa trên giới hạn ký tự và số dòng.

    Tham số:
    word_list (list): Danh sách các từ, có thể chứa '\\n' cho ngắt dòng.
    index_start (int): Chỉ số của từ bắt đầu trong danh sách.
    max_lines (int): Số dòng tối đa cho phép.
    max_chars_per_line (int): Số ký tự tối đa trên mỗi dòng.

    Trả về:
    tuple: Một tuple chứa (start_index, formatted_string).
           start_index là chỉ số đầu vào, formatted_string là chuỗi đã được sắp xếp.
    """
    # Khởi tạo các biến để theo dõi trạng thái
    lines = []
    current_line = ""
    line_count = 0
    index_end = index_start

    # Vòng lặp chính để xử lý các từ
    while index_end < len(word_list) and line_count < max_lines:
        current_word = word_list[index_end]

        # Xử lý trường hợp gặp ký tự xuống dòng '\\n'
        if current_word == "\n":
            lines.append(current_line)  # Kết thúc dòng hiện tại
            current_line = ""
            line_count += 1
            index_end += 1
            continue  # Chuyển sang từ tiếp theo ngay lập tức

        # Tính toán độ dài của dòng mới nếu thêm từ hiện tại
        if not current_line:
            # Nếu dòng trống, chỉ thêm từ vào
            new_line_length = len(current_word)
        else:
            # Nếu dòng đã có từ, thêm dấu cách trước khi thêm từ mới
            new_line_length = len(current_line) + 1 + len(current_word)

        # Kiểm tra xem từ có vừa với dòng không
        if new_line_length <= max_chars_per_line:
            # Nếu vừa, thêm từ vào dòng hiện tại
            if current_line:
                current_line += " " + current_word
            else:
                current_line = current_word
            index_end += 1
        else:
            # Nếu không vừa, kết thúc dòng hiện tại và bắt đầu dòng mới
            lines.append(current_line)
            current_line = ""
            line_count += 1
            # Không tăng 'i' để từ hiện tại được xử lý lại ở dòng tiếp theo

    # Thêm dòng cuối cùng nếu nó không rỗng sau khi vòng lặp kết thúc
    if current_line:
        lines.append(current_line)

    # Nối tất cả các dòng lại với nhau bằng ký tự xuống dòng
    formatted_string = "\n".join(lines)

    return formatted_string, index_end


def text_slicer_backward(word_list, index_end, max_lines, max_chars_per_line):
    """
    Sắp xếp các từ thành các dòng, bắt đầu từ một chỉ số kết thúc và đi ngược.

    Tham số:
    word_list (list): Danh sách các từ, có thể chứa '\\n'.
    index_end (int): Chỉ số của từ cuối cùng được sử dụng.
    max_lines (int): Số dòng tối đa cho phép.
    max_chars_per_line (int): Số ký tự tối đa trên mỗi dòng.

    Trả về:
    tuple: Một tuple chứa (index_start, formatted_string).
           index_start là chỉ số của từ đầu tiên được sử dụng.
           formatted_string là chuỗi văn bản đã được sắp xếp.
    """
    lines = []
    current_line = ""
    line_count = 0
    index_start = index_end

    # Vòng lặp chính để xử lý các từ từ cuối về đầu
    while index_start >= 0 and line_count < max_lines:
        current_word = word_list[index_start]

        # Xử lý trường hợp đặc biệt của một từ quá dài
        word_len = len(current_word)
        if current_line == "" and word_len > max_chars_per_line and current_word != "\n":
            break

        # Xử lý trường hợp gặp ký tự xuống dòng '\\n'
        if current_word == "\n":
            # Nếu dòng hiện tại không rỗng, thêm nó vào danh sách lines
            if current_line:
                lines.insert(0, current_line)
                current_line = ""
                line_count += 1
            # Thêm dòng trống đại diện cho '\n' thứ hai liên tiếp
            # (tức là khi gặp '\n' mà current_line đang rỗng)
            else:
                lines.insert(0, "")
                line_count += 1

            index_start -= 1
            continue

        # Tính toán độ dài của dòng mới nếu thêm từ hiện tại vào đầu dòng
        new_line = current_word + (" " + current_line if current_line else "")
        new_line_length = len(new_line)

        # Kiểm tra xem từ có vừa với dòng không
        if new_line_length <= max_chars_per_line:
            current_line = new_line
            index_start -= 1
        else:
            # Nếu không vừa, kết thúc dòng hiện tại và bắt đầu dòng mới
            lines.insert(0, current_line)
            current_line = ""
            line_count += 1

    # Thêm dòng cuối cùng nếu nó không rỗng
    if current_line:
        lines.insert(0, current_line)

    # Nối tất cả các dòng lại với nhau
    formatted_string = "\n".join(lines)

    # Chỉ số bắt đầu là chỉ số của từ đầu tiên được thêm vào
    index_start_result = index_start + 1

    return formatted_string, index_start_result

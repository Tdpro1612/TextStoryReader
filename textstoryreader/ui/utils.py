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

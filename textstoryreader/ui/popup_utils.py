from kivy.metrics import (
    dp,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def show_simple_popup(title, message):
    """
    Hiển thị một popup đơn giản. Hữu ích cho các thông báo chung.
    """
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

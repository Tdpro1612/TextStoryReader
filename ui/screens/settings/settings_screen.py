from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_font_size_change(self, instance, value):
        print(f"Kích thước chữ thay đổi: {int(value)}")
        # Thêm logic để áp dụng thay đổi kích thước chữ

    def on_theme_change(self, instance, value):
        theme = 'dark' if value else 'light'
        print(f"Chế độ theme thay đổi: {theme}")
        # Thêm logic để thay đổi theme ứng dụng
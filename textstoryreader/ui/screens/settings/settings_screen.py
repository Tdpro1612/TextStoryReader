import os

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider

from textstoryreader.models.settings import Settings
from textstoryreader.ui.utils import rgba_to_hex_6


class SettingsScreen(Screen):
    previous_screen: str = "library_screen"
    font_name = StringProperty("Roboto")
    font_size = NumericProperty(24)
    text_color = ListProperty([0, 0, 0, 1])  # RGBA
    background_color = ListProperty([1, 1, 1, 1])  # RGBA
    font_list = [f for f in os.listdir("textstoryreader/assets/fonts") if f.lower().endswith((".ttf", ".otf"))]

    def go_back(self):
        app = App.get_running_app()
        App.get_running_app().update_settings()
        if self.previous_screen == "reader_screen":
            reader_screen = app.root.get_screen("reader_screen")
            reader_screen.apply_settings()
            reader_screen.show_current_page()
            app.root.current = "reader_screen"
        else:
            app.root.current = self.previous_screen

    def save_settings(self):
        self.font_name = self.font_name.strip()
        self.text_color = self.text_color
        self.background_color = self.background_color
        self.font_size = max(10, min(self.font_size, 72))
        settings_new = Settings(
            font_name="textstoryreader/assets/fonts/" + self.font_name,
            font_size=self.font_size,
            text_color=rgba_to_hex_6(self.text_color),
            background_color=rgba_to_hex_6(self.background_color),
        )
        print(f"DEBUG settings_new: {settings_new}")
        app = App.get_running_app()
        app.managers.settings_manager.save_settings(settings_object=settings_new)
        app.update_settings()

    def reset_settings(self):
        app = App.get_running_app()
        app.managers.settings_manager.save_settings(settings_object=Settings())
        app.update_settings()

    def open_color_picker(self, color_property):
        """Tạo và hiển thị một popup bảng màu."""
        content = BoxLayout(orientation="vertical", padding="10dp", spacing="10dp")

        # Tiêu đề Popup
        popup_title = Label(text="Chọn Màu")
        content.add_widget(popup_title)

        # Lấy giá trị màu ban đầu
        if color_property == "text_color":
            initial_color = self.text_color
        else:
            initial_color = self.background_color

        # Tạo thanh trượt cho các kênh màu
        sliders = {}
        for i, color_name in enumerate(["Red", "Green", "Blue", "Alpha"]):
            box = BoxLayout(spacing="10dp")
            label = Label(text=f"{color_name}:")
            slider = Slider(min=0, max=1, value=initial_color[i])
            box.add_widget(label)
            box.add_widget(slider)
            content.add_widget(box)
            sliders[color_name] = slider

        # Tạo một box hiển thị màu hiện tại trong popup
        preview_box = BoxLayout(size_hint_y=None, height="50dp")
        content.add_widget(preview_box)

        def update_preview(_instance, _value):
            """Cập nhật màu của preview box dựa trên giá trị thanh trượt."""
            with preview_box.canvas.before:
                preview_box.canvas.before.clear()
                Color(sliders["Red"].value, sliders["Green"].value, sliders["Blue"].value, sliders["Alpha"].value)
                Rectangle(pos=preview_box.pos, size=preview_box.size)

        for slider in sliders.values():
            slider.bind(value=update_preview)

        # Cập nhật màu ban đầu cho preview box
        update_preview(None, None)

        # Nút xác nhận
        ok_button = Button(text="OK", size_hint_y=None, height="40dp")
        content.add_widget(ok_button)

        # Tạo popup
        popup = Popup(title="Chọn màu", content=content, size_hint=(0.9, 0.7), auto_dismiss=False)

        def apply_color(_instance):
            """Lấy giá trị từ các thanh trượt và gán cho thuộc tính màu của màn hình."""
            new_color = [sliders["Red"].value, sliders["Green"].value, sliders["Blue"].value, sliders["Alpha"].value]
            if color_property == "text_color":
                self.text_color = new_color
            else:
                self.background_color = new_color
            popup.dismiss()

        ok_button.bind(on_release=apply_color)

        popup.open()

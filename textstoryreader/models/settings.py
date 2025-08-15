from dataclasses import dataclass


@dataclass
class Settings:
    font_name: str = "Roboto"
    font_size: int = 24
    text_color: str = "#000000"
    background_color: str = "#FFFFFF"
    line_spacing: float = 1.2

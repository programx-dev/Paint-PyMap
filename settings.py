from PyQt6.QtGui import QColor
from dataclasses import dataclass, field
import copy
from dataclasses import dataclass, field

"""Это модуль с настройками, тут можно добавить свои настройки при реализации нового инструмента"""

def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))


@dataclass
class BrushSettings:
    width: int = 3
    width_range: tuple[int] = (1, 3, 5, 7, 10)


@dataclass
class SpraySettings:
    width: int = 10
    width_range: tuple[int] = (5, 10, 15, 20, 25)
    density: int = 0.4



@dataclass
class FigureSettings:
    width: int = 3
    width_range: tuple[int] = (1, 3, 5, 7, 10)


@dataclass
class Settings:
    primary_color: QColor = default_field(QColor("#000000"))
    brush: BrushSettings = BrushSettings
    spray: FigureSettings = SpraySettings
    figure: FigureSettings = FigureSettings

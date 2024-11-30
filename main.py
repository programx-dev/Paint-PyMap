import sys
import os
from PyQt6 import QtWidgets
from PyQt6.QtGui import QMouseEvent, QPixmap, QImage, QColor, QIcon, QAction
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
import typing
import drawing
from settings import Settings
from style import style_sheet
from icons.icon import icon

__author__ = "https://t.me/PyMapChannel"

"""Это главный модуль
Для добавления нового инструмента из drawing.py, нужно:
в классе ToolBar добавить кортеж из пути к иконке инструмента и класс нового инструмента"""

# УСТАНОВКА ЗАВИСЕМОСТЕЙ: pip install PyQt6


class ScrollLabel(QtWidgets.QScrollArea):
    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)

        self.label = QtWidgets.QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setWidget(self.label)

    def setPixmap(self, pixmap: QPixmap):
        self.label.setPixmap(pixmap)

        self.update()


class Palette(QtWidgets.QWidget):
    colors = [
        "#000000", "#808080", "#800000", "#FF0000", "#008000", "#00FF00",
        "#808000", "#FFFF00", "#000080", "#0000FF", "#800080", "#FF00FF", "#008080",
        "#00FFFF", "#C0C0C0", "#FFFFFF"
    ]
    color_choosed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        self.primary_color_button = QtWidgets.QPushButton()
        self.primary_color_button.pressed.connect(self.choose_custom_color)
        self.primary_color_button.setObjectName("primary_color_button")
        self.primary_color_button.setFixedSize(34, 34)

        self.grid_layout.addWidget(self.primary_color_button, 0, 0, 2, 1, Qt.AlignmentFlag.AlignCenter)

        self.init_button = None
        self.primary_color = QColor()

        for i, color in enumerate(Palette.colors):
            button = self.PaletteButton(color)
            button.color_choosed.connect(self.choose_new_color)

            if i == 0:
                self.init_button = button

            self.grid_layout.addWidget(button, i % 2, i // 2 + 1)

    def choose_custom_color(self):
        color_dialog = QtWidgets.QColorDialog()
        color = color_dialog.getColor(self.primary_color)

        if color.isValid():
            self.primary_color = color

            self.set_style_color_button()

            self.color_choosed.emit()

    def choose_new_color(self):
        self.primary_color = self.sender().color

        self.set_style_color_button()

        self.color_choosed.emit()

    def set_style_color_button(self):
        self.primary_color_button.setStyleSheet(f"""#primary_color_button {{
            background-color: {self.primary_color.name()};
        }}""")

    class PaletteButton(QtWidgets.QPushButton):
        color_choosed = pyqtSignal()

        def __init__(self, color: str):
            super().__init__()

            self.color = QColor(color)
            self.str_color = color

            self.setFixedSize(QSize(22, 22))
            self.setObjectName("palette_button")
            self.clicked.connect(self._color_choosed)

            self.setStyleSheet(f"""#palette_button {{
                background-color: {self.str_color};
            }}""")

        def _color_choosed(self):
            self.color_choosed.emit()


class VerticalSeparator(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("separator")

        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.setFixedWidth(1)


class HorizontalSeparator(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("separator")

        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setFixedHeight(1)


class ToolBar(QtWidgets.QWidget):
    prew_button = None
    tool_choosed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.grid_layout_tool = QtWidgets.QGridLayout()
        self.grid_layout_tool.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout_tool.setSpacing(2)
        self.grid_layout_tool.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout_tool)

        self.tool = None

        tools = [
            (drawing.Brush, "./icons/pencil.png"),
            (drawing.Fill, "./icons/can.png"),
            (drawing.Spray, "./icons/spray.png"),
            (drawing.Line, "./icons/line.png"),
            (drawing.Rectangle, "./icons/rectangle.png"),
            (drawing.Ellipse, "./icons/ellipse.png")
        ]

        self.init_button = None

        for i, arg in enumerate(tools):
            button = self.ToolButton(*arg)
            button.tool_choosed.connect(self._tool_choosed)

            if i == 0:
                self.init_button = button

            self.grid_layout_tool.addWidget(button, 1 + i % 2, i // 2)

    def _tool_choosed(self):
        if ToolBar.prew_button is None:
            ToolBar.prew_button = self.sender()
            ToolBar.prew_button.set_style_selected()

        else:
            ToolBar.prew_button.set_style_normal()
            ToolBar.prew_button = self.sender()
            ToolBar.prew_button.set_style_selected()

        self.tool = ToolBar.prew_button.tool

        self.tool_choosed.emit()

    class ToolButton(QtWidgets.QPushButton):
        tool_choosed = pyqtSignal()

        def __init__(self, tool: typing.Type, image: str):
            super().__init__()

            self.tool = tool
            self.image = QIcon(image)

            self.setFixedSize(QSize(32, 32))
            self.setObjectName("tool_button")
            self.setProperty("state", "normal")
            self.setIcon(self.image)
            self.clicked.connect(self._tool_choosed)

            self.set_style_normal()

        def _tool_choosed(self):
            self.tool_choosed.emit()

        def set_style_normal(self):
            self.setProperty("state", "normal")

            self.setStyle(self.style())

        def set_style_selected(self):
            self.setProperty("state", "selected")

            self.setStyle(self.style())


class SizeCombobox(QtWidgets.QComboBox):
    size_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setObjectName("size_combobox")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.currentIndexChanged.connect(self.changed_size)

        self.view().window().setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def add_items(self, items: list[int], current_index: int):
        self.blockSignals(True)
        self.clear()

        for i in items:
            self.addItem(f"{i} пкс", i)

        self.blockSignals(False)
        self.setCurrentIndex(current_index)

    def changed_size(self, item: int):
        self.size_changed.emit(self.itemData(item))


class Canvas(ScrollLabel):
    def __init__(self):
        super().__init__()

        self.img_width = 1200
        self.img_height = 600

        self.setObjectName("canvas")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        self.new_image(self.img_width, self.img_height)

        self.drawing = False
        self.settings = Settings()
        self.last_point = QPoint()
        self.tool: drawing.BaseTool = None

    def open_image(self, path: str):
        self.image = QImage(path)

        self.setPixmap(QPixmap.fromImage(self.image))

    def new_image(self, width: int, height: int):
        self.img_width = width
        self.img_height = height

        self.image = QImage(width, height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

        self.setPixmap(QPixmap.fromImage(self.image))

    def update_tool(self, tool: type = None):
        tool = tool or self.tool.__class__

        self.tool = tool(self.settings)
    
    def update_tool_width(self, width: int):
        tool_class: drawing.BaseTool = self.tool.__class__

        tool_settings_field = getattr(tool_class, "settings_field", None)

        tool_settings = None
        if tool_settings_field is not None:
            tool_settings = getattr(self.settings, tool_settings_field, None)

        if tool_settings and tool_settings.width and tool_settings.width_range:
            tool_settings.width = width

            self.update_tool()

    def update_primary_color(self, primary_color: QColor):
        self.settings.primary_color = primary_color

        self.update_tool()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = self.get_point(event.pos())

            new_image = self.tool.mouse_press_event(self.image, self.last_point)

            self.setPixmap(QPixmap.fromImage(new_image))

    def mouseMoveEvent(self, event: QMouseEvent):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            new_image = self.tool.mouse_move_event(self.image, self.last_point, self.get_point(event.pos()))

            self.last_point = self.get_point(event.pos())

            self.setPixmap(QPixmap.fromImage(new_image))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

            new_image = self.tool.mouse_release_event(self.image, self.get_point(event.pos()))

            self.setPixmap(QPixmap.fromImage(new_image))

    def get_point(self, point: QPoint):
        return point + QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        pixmap = QPixmap()
        QPixmap.loadFromData(pixmap, icon)

        self.setWindowTitle("Paint by Python Map")
        self.setWindowIcon(QIcon(pixmap))

        self.menubar = self.menuBar()

        self.new_action = QAction("Создать")
        self.new_action.triggered.connect(self.new_image)

        self.open_action = QAction("Открыть")
        self.open_action.triggered.connect(self.open_image)

        self.save_action = QAction("Сохранить как")
        self.save_action.triggered.connect(self.save_image)

        self.file_menu = self.menubar.addMenu("Файл")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)

        self.widget = QtWidgets.QFrame()
        self.widget.setObjectName("widget")
        self.setCentralWidget(self.widget)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setRowStretch(1, 1)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.widget.setLayout(self.grid_layout)

        self.toolbar_layout = QtWidgets.QHBoxLayout()
        self.toolbar_layout.setContentsMargins(10, 5, 10, 5)
        self.toolbar_layout.setSpacing(10)
        self.grid_layout.addLayout(self.toolbar_layout, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)

        self.toolbar = ToolBar()
        self.toolbar_layout.addWidget(self.toolbar)
        self.toolbar_layout.addWidget(VerticalSeparator())

        self.size_combobox = SizeCombobox()
        self.size_combobox.size_changed.connect(self.size_combobox_changed)
        self.toolbar_layout.addWidget(self.size_combobox)
        self.toolbar_layout.addWidget(VerticalSeparator())

        self.pallete = Palette()
        self.toolbar_layout.addWidget(self.pallete)

        self.canvas_layout = QtWidgets.QVBoxLayout()
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas_layout.setSpacing(0)
        self.grid_layout.addLayout(self.canvas_layout, 1, 0)

        self.canvas = Canvas()
        self.canvas_layout.addWidget(HorizontalSeparator())
        self.canvas_layout.addWidget(self.canvas)

        self.toolbar.tool_choosed.connect(self.change_tool)
        self.pallete.color_choosed.connect(self.change_primary_color)

        self.toolbar.init_button._tool_choosed()
        self.pallete.init_button._color_choosed()

        self.setStyleSheet(style_sheet)

    def new_image(self):
        width, status = QtWidgets.QInputDialog.getInt(self, "Ширина холста", "Введите ширину холста [50; 1820]",
                                                        min = 50, max=1820, value=self.canvas.img_width)

        if not status:
            return

        height, status = QtWidgets.QInputDialog.getInt(self, "Высота холста", "Введите высоту холста [50; 1820]",
                                                      min=50, max=1820, value=self.canvas.img_height)
                                                      
        self.canvas.new_image(width, height)
        
    def save_image(self):
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))

        dialog = QtWidgets.QFileDialog()
        path, _ = dialog.getSaveFileName(self, "Сохранить изображение", desktop, "PNG(*.png);;JPG(*.jpg)")

        if path:
            self.canvas.image.save(path)

    def open_image(self):
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))

        dialog = QtWidgets.QFileDialog()
        path, _ = dialog.getOpenFileName(self, "Открыть изображение", desktop, "PNG(*.png);;JPG(*.jpg)")

        if path:
            self.canvas.open_image(path)

    def size_combobox_changed(self, value: int):
        self.canvas.update_tool_width(value)

    def size_value_changed(self, value: int):
        self.canvas.update_tool_width(value)

    def change_tool(self):
        tool = self.sender().tool

        self.canvas.update_tool(tool)

        tool_class: drawing.BaseTool = self.canvas.tool.__class__

        tool_settings_field = getattr(tool_class, "settings_field", None)

        tool_settings = None
        if tool_settings_field is not None:
            tool_settings = getattr(self.canvas.settings, tool_settings_field, None)

        if tool_settings_field and tool_settings.width and tool_settings.width_range:
            self.size_combobox.setEnabled(True)
            self.size_combobox.add_items(tool_settings.width_range,
                                         tool_settings.width_range.index(tool_settings.width))
        else:
            self.size_combobox.setEnabled(False)

    def change_primary_color(self):
        self.canvas.update_primary_color(self.sender().primary_color)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()

    app.exec()

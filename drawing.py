from PyQt6.QtGui import QPainter, QPen, QImage, QPixmap
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF
import random
from settings import Settings

"""В этом модуле можно создать свои инструменты для рисования
Для этого нужно реализовать методы: 
        __init__ (принимает настройки), 
        mouse_press_event (принимает ссылку на изображение и текущую точку) -> ссылку на изображение
        mouse_move_event (принимает ссылку на изображение, старую точку и текущую точку) -> ссылку на изображение
        mouse_release_event (принимает ссылку на изображение и текущую точку) -> ссылку на изображение

Если нужно нарисовать фигуру, то можно создать копию текущего изображения и рисовать на ней то, как изменяется размер фигуры,
сохранив при этом исходное, затем при отпускании в методе mouse_release_event можно нарисовать итоговую фигуру"""


class BaseTool:
    settings_field = None

    def __init__(self):
        self.color = None
        self.width = None
        self.range = None

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        return image

    def mouse_release_event(self, image: QImage, point: QPoint) -> QImage:
        return image


class Brush(BaseTool):
    settings_field = "brush"

    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color
        self.width = settings.brush.width
        self.range = settings.brush.width_range

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        painter.drawPoint(point)

        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        painter.drawLine(last_point, point)

        return image


class Fill(BaseTool):
    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, 1))

        if self.color == image.pixel(point):
            return image

        w, h = image.width(), image.height()
        x, y = point.x(), point.y()
        s = image.bits().asstring(w * h * 4)

        def get_pixel(x, y):
            i = (x + (y * w)) * 4
            return s[i:i+3]

        target_color = get_pixel(x, y)

        def get_cardinal_points(have_seen, center_pos):
            points = []
            cx, cy = center_pos
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                xx, yy = cx + x, cy + y
                if (
                    xx >= 0
                    and xx < w
                    and yy >= 0
                    and yy < h
                    and (xx, yy) not in have_seen
                ):
                    points.append((xx, yy))
                    have_seen.add((xx, yy))

            return points

        have_seen = set()
        queue = [(x, y)]

        while queue:
            x, y = queue.pop()
            if get_pixel(x, y) == target_color:
                painter.drawPoint(QPoint(x, y))
                queue.extend(get_cardinal_points(have_seen, (x, y)))

        return image


class Rectangle(BaseTool):
    settings_field = "figure"

    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color
        self.width = settings.figure.width
        self.range = settings.figure.width_range
        self.start_point = QPoint()

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        self.start_point = point

        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        """Мы делаем копию изображения для того чтобы на нем показывать, что изменяется размер фигуры. 
            А само оригинальное изображения измениться только в методе self.mouse_release_event"""
        image = QImage(image)
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawRect(QRect(self.start_point, point))

        return image

    def mouse_release_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawRect(QRect(self.start_point, point))

        return image


class Ellipse(BaseTool):
    settings_field = "figure"

    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color
        self.width = settings.figure.width
        self.range = settings.figure.width_range
        self.point_start = QPoint()

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        self.point_start = point

        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        image = QImage(image)
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawEllipse(QRect(self.point_start, point))

        return image

    def mouse_release_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawEllipse(QRect(self.point_start, point))

        return image


class Line(BaseTool):
    settings_field = "figure"

    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color
        self.width = settings.figure.width
        self.range = settings.figure.width_range
        self.point_start = QPoint()

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        self.point_start = point

        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        image = QImage(image)
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawLine(self.point_start, point)

        return image

    def mouse_release_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin))

        painter.drawLine(self.point_start, point)

        return image


class Spray(BaseTool):
    settings_field = "spray"

    def __init__(self, settings: Settings):
        super().__init__()

        self.color = settings.primary_color
        self.width = settings.spray.width
        self.range = settings.spray.width_range
        self.density = settings.spray.density

    def mouse_press_event(self, image: QImage, point: QPoint) -> QImage:
        painter = QPainter(image)
        painter.setPen(QPen(self.color, 1, cap=Qt.PenCapStyle.RoundCap))

        square = 3.14 * (self.width // 2) ** 2
        count_points = int(square * self.density)

        for _ in range(count_points):
            x = random.gauss(0, self.width//2)
            y = random.gauss(0, self.width//2)

            pointn = QPointF(point.x() + x, point.y() + y)
            painter.drawPoint(pointn)

        return image

    def mouse_move_event(self, image: QImage, last_point: QPoint, point: QPoint) -> QImage:
        return self.mouse_press_event(image, point)

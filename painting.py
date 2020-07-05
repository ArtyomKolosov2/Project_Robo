# -*- coding: utf-8 -*-
from math import cos, sin

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import (QPainter, QPen, QColor, QFont)
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit,
                             QPushButton, QLabel)


class Paint(QWidget):
    points_one = ()
    points_two = ()
    signal = pyqtSignal(int)  # Обьявление сигналов
    end_angle_signal = pyqtSignal(int)
    end_radius_signal = pyqtSignal(int)

    def __init__(self, scara, parent=None):  # Конструрктор класса, передача ему объекта класса Scara
        super(Paint, self).__init__(parent)
        self.sc = scara
        self.cases = []
        # for i in range(5): Остатки от разработки элеметов, которые переносит робот
        #     self.cases.append(Case("1.{0}.6.7.{1}.10.11.12.13".format(i + 4, i)))
        self.LENGTH = self.sc.LENGTH  # Длинна манипулятора
        self.ONERAD = self.sc.ONERAD  # Значение для перевода градусов в радианы
        self.hand = self.sc.hand
        self.R1 = self.sc.R1
        self.R2 = self.sc.R2
        if self.R2 > self.sc.LENGTH:
            self.R2 = int(self.sc.LENGTH)
        self.current_radius = self.R2
        self.current_angle = 0  # Текущий угол
        self.angle_to_go = 0  # След. угол
        self.radius_to_go = 0  # След. радиус
        self.current_angle = 0  # Текущий радиус
        self.current_point = 1  # Текущая точка автомата
        self.operation = 1

        self.change_flag = True
        self.rewrite_flag = False
        self.clicked_flag = False
        self.automat_flag = False  # Флаг автомат движения
        self.go_to_a_flag = False  # Флаги, куда движется манип. a = к след. углу
        self.go_to_r_flag = False  # Флаги, куда движется манип. r = к след. радиусу

        self.aspect_x = 3  # Отношения центровки изображения манипулятора
        self.aspect_y = 2  #
        self.angle = 1
        self.w = 0  # Ширина экрана
        self.h = 0  # Высота экрана
        self.fi = 0
        self.stripe = 0
        self.lastPos_x = 0
        self.lastPos_y = 0

        self.user_interface()

    def user_interface(self):

        self.timer = QTimer()  # Инициализация таймера, который будет исп. для анимации

        self.btn = QPushButton("PushToCoord", self)
        self.btn.setGeometry(650, 20, 120, 40)
        self.btn.clicked.connect(self.start)
        self.btn.hide()

        self.btn_krug = QPushButton("Push", self)
        self.btn_krug.setGeometry(650, 130, 120, 40)
        self.btn_krug.clicked.connect(self.step)

        self.lineEd = QLineEdit(self)
        self.lineEd.setGeometry(660, 100, 100, 20)

        self.lab = QLabel(self)
        self.lab.setGeometry(648, 60, 120, 43)
        self.lab.setStyleSheet("QLabel{font:20px Arial bold;}")
        self.lab.setText("Масштаб 1:{0}".format(self.sc.scale))

        self.resize(900, 700)  # Установка размров окна
        self.setWindowTitle("RobotDrawing")
        self.show()

    def start(self):
        pass

    def get_offset_x(self):  # Получение смещения по x
        return round(self.width() / self.aspect_x, 2)

    def get_offset_y(self):  # Получение смещения по y
        return round(self.height() / self.aspect_y, 2)

    def step(self):
        new_angle = self.lineEd.text()
        if new_angle.isdigit():
            new_angle = int(new_angle)
            if 0 < new_angle < 91 and not 360 % new_angle:
                self.angle = new_angle
                self.change_flag = True
        self.lineEd.clear()
        self.update()

    def resizeEvent(self, e):  # При изменении размеров окна мы перерисовываем манипулятор
        self.change_flag = True

    def ret_mas(self, radius, angle=45, width=0, height=0):  # Возврощает лист, который содержит каждую координаты
        # каждой точки окружности
        arr = []
        for a in range(0, 361, angle):
            a *= self.sc.ONERAD
            arr.append(self.sc.get_real_cor(a, radius, width, height))
        return tuple(arr)

    def paintEvent(self, e):  # PaintEvent вызывается при любом изменении окна
        # Функция, отвечающая за отрисовку

        qp = QPainter()  # Класс, отвичающий за рисование
        qp.begin(self)  # Обьявление начал рисования
        qp.setRenderHint(QPainter.Antialiasing)  # Установка сглаживания на текст и на рисунок
        qp.setRenderHint(QPainter.TextAntialiasing)
        qp.setFont(QFont("Arial", 13))

        if self.current_angle < 0:
            self.current_angle = 360

        elif self.current_angle > 360:
            self.current_angle = 0

        if self.change_flag:  # Проверка флага, который отвечет нужно ли заново получать координаты окружности
            # Так сделано для экономии ресурсов
            self.w = self.get_offset_x()
            self.h = self.get_offset_y()

            self.points_one = self.ret_mas(self.R1, self.angle, self.w, self.h)
            self.points_two = self.ret_mas(self.R2, self.angle, self.w, self.h)

            self.change_flag = False

        self.draw_circle(qp, self.points_one)  # Отрисовка окружностей
        self.draw_circle(qp, self.points_two)
        self.draw_stripes(qp, self.R2)  # Отрисовка лучей

        if self.rewrite_flag:
            if not self.current_angle >= len(self.points_two):
                self.rewrite_flag = False
            else:
                self.current_angle = 0

        self.draw_robot(qp,  # Рисование манипулятора, функция принимает обьект класса, радиус, угол, руку, и кординаты
                        self.current_radius,
                        x=self.lastPos_x,
                        y=self.lastPos_y,
                        alpha=self.current_angle,
                        hand=self.hand)

        self.signal.emit(0)  # Сигнал для обновляния данных в base.QTextEdit
        if isinstance(self.cases, list) and not self.cases is []:
            self.draw_case(qp)
        self.draw_text_point(qp)  # Отрисовка номеров точек
        qp.end()  # Конец рисования

    def draw_case(self, qp):  # Отрисовка содержимого контейнеров для перемещения, для активации раскоменьтить код на
        # строках 23-24
        angle = 0
        for case in self.cases:
            offset = 0
            cor = self.sc.get_real_cor(-angle * self.sc.ONERAD, self.R2, self.w, self.h)
            for point in case.circle_pos:
                offset += 1
                if point:
                    qp.drawEllipse(cor[0] - 10 + offset, cor[1] - 10, 20, 20)
            angle += 45

    def go_to_angle(self):  # анимация перехода на другой угол
        if self.current_angle == self.angle_to_go:
            if self.current_angle >= 360:
                self.current_angle = 0
            self.go_to_a_flag = False
            if self.go_to_r_flag and self.automat_flag:
                self.end_angle_signal.emit(1)  # Генерация сигналов для автомата
            elif self.automat_flag:
                self.end_angle_signal.emit(2)
            return None

        self.current_angle += self.operation

        self.timer.singleShot(self.sc.NS, self.go_to_angle)  # Таймер, задающий скорость анимации
        self.update()  # Метод обновления окна, он вызывает paintEvent для отображения новых данных

    def go_to_radius(self):  # анимация перехода на другой радиус
        if self.current_radius == self.radius_to_go:
            self.go_to_r_flag = False
            if self.automat_flag:
                self.end_radius_signal.emit(2)
            return None

        if not self.go_to_a_flag:
            if self.current_radius < self.radius_to_go:
                self.current_radius += 1
            else:
                self.current_radius -= 1

        self.timer.singleShot(self.sc.NS, self.go_to_radius)
        self.update()

    def draw_robot(self, qp, radius, x=0, y=0, alpha=0, hand=0):  # Главный метод для отрисовки манипулятора
        pen = QPen(QColor(128, 0, 0), 2)  # Устанавливаем цвет ручки
        qp.setPen(pen)
        if x and y:  # Если переданы x и y то, функция будет использовать их для просчета коорд манипулятора
            alpha = self.sc.calculate_angle(x, y, self.w, self.h)
            radius = round(((x - self.w) / cos(alpha)))
            self.lastPos_y = 0
            self.lastPos_x = 0
            if radius > self.sc.LENGTH:
                radius = self.sc.LENGTH

        elif alpha:  # Если передан угол, то исп. его для отрисовки
            alpha *= self.sc.ONERAD
            alpha = -alpha  # Угол с отриц. значением для правильного отображения, т.к. рабочая область в модуле ,
            # используемом для отображения перевёрнута
        self.current_angle = -round((alpha * self.sc.ONEGRAD))
        self.stripe = radius - self.sc.a3  # Высчитываем сторону треуг. нужную для расчета
        self.fi = self.sc.inverse_problem(self.stripe,  # Высчитываем угол манипулятора
                                          angle=alpha,
                                          hand=hand)

        first_points = self.sc.get_real_cor(self.fi, self.sc.a1, self.w, self.h)  # Получаем точку начала первого рычага
        second_points = self.sc.get_real_cor(alpha, self.stripe, self.w, self.h)  # Получаем точку начала второго рычага
        third_points = self.sc.get_real_cor(alpha, radius, self.w, self.h)  # Получаем точку начала третьего рычага

        qp.drawEllipse(self.w - 5,
                       self.h - 5,
                       10,
                       10)

        qp.drawLine(self.w,  # Отрисовка рычагов
                    self.h,
                    first_points[0],
                    first_points[1])

        qp.drawEllipse(first_points[0] - 5,
                       first_points[1] - 5,
                       10,
                       10)
        qp.drawLine(first_points[0],  # Отрисовка рычагов
                    first_points[1],
                    second_points[0],
                    second_points[1])

        qp.drawEllipse(second_points[0] - 5,
                       second_points[1] - 5,
                       10,
                       10)

        qp.drawLine(second_points[0],  # Отрисовка рычагов
                    second_points[1],
                    third_points[0],
                    third_points[1])

    def draw_stripes(self, qp, radius):  # Функция отрисовки лучей
        pen = QPen(QColor(0, 128, 0), 1)
        qp.setPen(pen)
        for i in range(0, 361, 45):
            i *= self.ONERAD
            qp.drawLine(self.w,
                        self.h,
                        radius * round(cos(i), 3) + self.w,
                        radius * round(sin(i), 3) + self.h)

    def draw_circle(self, qp, point):  # Отрисовка круга по точкам
        pen = QPen(QColor(0, 128, 0), 2)
        qp.setPen(pen)
        for i in range(len(point)):
            if i != 0:
                qp.drawLine(point[i - 1][0],
                            point[i - 1][1],
                            point[i][0],
                            point[i][1])

    def draw_text_point(self, qp):  # Отрисовка номеров точек
        pen = QPen(QColor(0, 0, 128), 2)
        qp.setPen(pen)
        index = 1
        for i in range(0, 360, 45):
            if i % 45 == 0:
                i *= -self.ONERAD
                x = cos(i) * (self.R1 + 14) + self.w - 3
                y = sin(i) * (self.R1 + 14) + self.h + 5
                qp.drawText(x, y, str(index))

                x = cos(i) * (self.R2 + 14) + self.w - 5
                y = sin(i) * (self.R2 + 14) + self.h + 5
                qp.drawText(x, y, str(index + 10))

                index += 1


if __name__ == "__main__":
    import sys, Scara

    sc = Scara.Scara(com="1")
    app = QApplication(sys.argv)
    window = Paint(sc)
    window.btn.show()
    window.setWindowTitle("RobotDrawing")
    sys.exit(app.exec_())

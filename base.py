# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox,
                             QLineEdit, QTabWidget)  # Импорт библиотек
from PyQt5.QtCore import Qt
import painting  # Импорт описанных классов
import Scara


class WidgetSteps(QWidget):  # Создание класса меню
    def __init__(self, index, parent=None):  # Конструктор класса
        super(WidgetSteps, self).__init__(parent)  # Наследование методов родительского класса
        self.sc = Scara.Scara(com="1")  # Инициализация класса, отвечающего за расчёты
        self.expected_signals = 0
        self.number_signals = 0
        self.index = index
        self.automat_index = 0
        self.paint = painting.Paint(self.sc)  # Инициализация класса, отвечающего за отрисовку
        self.paint.signal.connect(self.update_info, Qt.QueuedConnection)  # Подключаем функции к сигналам из painting
        self.paint.end_angle_signal.connect(self.next_point, Qt.QueuedConnection)
        self.paint.end_radius_signal.connect(self.next_point, Qt.QueuedConnection)
        self.control = WidgetControl()  # Инициализируем виджет с основынми упр. элементами
        self.waiting_for_stop = False
        self.Ui()

    def Ui(self):

        self.group_box = QGroupBox("Управление-{0}".format(self.index))
        self.group_box.setStyleSheet("QGroupBox{border: 2px solid orange;"  # Меняем вид при помощи HTML тегов
                                     "font: Arial;}")

        self.btn_auto = QPushButton("&Автомат")  # Инициализация кнопок и присовение им имён
        self.btn_auto.clicked.connect(self.on_change_auto)

        self.btn_manual = QPushButton("&Ручной Режим")
        self.btn_manual.clicked.connect(self.on_change_man)

        self.btn_step = QPushButton("Шаг")
        self.btn_step.clicked.connect(self.paint.start)
        self.btn_step.hide()

        self.text_edit = QTextEdit()  # Создание строки для ввода данных
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("QTextEdit{font:15px Arial;}")

        self.table = QTableWidget()  # Создание таблицы
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["x", "y"])

        self.control.btn.clicked.connect(self.get_angle_to)  # Подключение кнопок к функциям
        self.control.btn_r.clicked.connect(self.get_radius_to)
        self.control.btn_r_one.clicked.connect(self.set_r_one)
        self.control.btn_r_two.clicked.connect(self.set_r_two)
        self.control.btn_a_plus.clicked.connect(self.step_a_plus)
        self.control.btn_a_minus.clicked.connect(self.step_a_minus)

        vbox = QVBoxLayout()  # Создание слоев интерфейса, нужно для
        vbox.addWidget(self.table)  # того, чтобы интерфейс динамически подстраивался
        vbox.addWidget(self.control)  # под размеры окна

        vbox1 = QVBoxLayout(self)
        vbox1.addSpacing(7)
        vbox1.addWidget(self.btn_auto)
        vbox1.addWidget(self.btn_manual)
        vbox1.addWidget(self.btn_step)
        vbox1.addWidget(self.text_edit)

        self.group_box.setLayout(vbox1)  # Установка слоя для виджета

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.group_box)
        hbox.addLayout(vbox)

        self.setLayout(hbox)  # Установка слоя для всего окна
        self.set_table_items()

    def update_info(self):
        self.text_edit.clear()
        fi = -round(self.paint.fi, 2)
        angle = self.paint.current_angle  # Получаем текущий угол манипулятора
        radius = self.paint.current_radius  # Получам текущий радиус на конце манипулятора
        cord = self.sc.get_real_cor(angle * self.sc.ONERAD,
                                    radius)  # Высчитываем координаты коцна манипулятора

        self.text_edit.insertPlainText("Угол 1 = {0}°\n"
                                       "Угол fi = {1}рад\n"  # Отображаем информацию 
                                       "Radius = {2}\n"
                                       "x = {3}\n"
                                       "y = {4}\n"
                                       "Next p = {5}".format(angle,
                                                             fi,
                                                             radius,
                                                             cord[0],
                                                             cord[1],
                                                             self.sc.coords[self.automat_index]))

    def get_angle_to(self):  # Получаем угол из ввода пользователя
        if self.paint.go_to_a_flag or self.paint.automat_flag:
            return None
        angle = self.control.lineEd1.text()  # Возвращает строковый тип данных
        self.control.lineEd1.clear()  # Отчищаем строку ввода
        if not angle.isdigit():  # делаем проверку, если ввод не числовой, то выходим из функции
            return None
        angle = int(angle)  # Перевод угла в число
        if angle > 360:  # Приводим угол в диапазон [0, 360]
            angle -= ((angle // 360) * 360)

        operation = self.calculate_operation(self.paint.current_angle, angle)  # Высчитываем направление,
        # Куда будет двигаться манипулятор

        self.start_change_angle(angle, operation)  # Вызываем функцию, начинающую изменение

    @staticmethod
    def calculate_operation(angle, angle_to_go):  # Высчитывание направление операции
        check = angle - angle_to_go  # Манипулятор выбирает наименьший путь для достижения своей цели
        if 0 > check > -180:
            operation = 1
        elif -360 <= check <= -180:
            operation = -1
        elif check > 180:
            operation = 1
        elif check <= 180:
            operation = -1
        return operation

    def step_a_plus(self):  # Передвигает манипулятор на +45 градусов
        if not self.paint.automat_flag:
            angle = self.paint.current_angle + 45
            if angle > 360:
                angle -= 360
            self.start_change_angle(angle, 1)

    def step_a_minus(self):  # Передвигает манипулятор на -45 градусов
        if not self.paint.automat_flag:
            angle = self.paint.current_angle - 45
            if angle < 0:
                angle += 360
            self.start_change_angle(angle, -1)

    def set_r_one(self):  # Передвигает конец манипулятора на первый радиус
        if not self.paint.automat_flag:
            self.start_change_radius(self.paint.R1)

    def set_r_two(self):  # Передвигает конец манипулятора на второй радиус
        if not self.paint.automat_flag:
            self.start_change_radius(self.paint.R2)

    def get_radius_to(self):  # Получаем радиус из строки вводв
        radius = self.control.lineEd2.text()
        self.control.lineEd2.clear()
        if not radius.isdigit() or self.paint.automat_flag:
            return None
        radius = int(radius) / self.sc.scale
        if radius > self.sc.LENGTH or radius <= 0:
            return None
        self.start_change_radius(radius)  # Вызов функции изменения радиуса

    def start_change_radius(self, radius):
        if self.paint.go_to_r_flag and not self.paint.automat_flag:  # Проверка на выполнение
            return None
        self.paint.radius_to_go = radius
        self.paint.go_to_r_flag = True
        self.paint.go_to_radius()  # Вызов функции, анимирующей перемещение
        self.paint.update()

    def start_change_angle(self, angle, operation):
        if self.paint.go_to_a_flag:  # Если уже идет выполнение, то выходим из функции
            return None
        self.paint.go_to_a_flag = True
        self.paint.operation = operation
        self.paint.angle_to_go = angle
        self.paint.go_to_angle()  # Вызов функции, анимирующей перемещение
        self.paint.update()

    def next_point(self, check=0):  # Функция перехода на след. точку автомата
        # time.sleep(0.5)

        if check == 1:  # проверка контрольной велечины, если 1, то меняем радиус
            # Если 2, то переходим на след. точку
            # Нужно для того, чтобы одновременно не менять угол и радиус,
            # А делать это одно за другим
            self.start_change_radius(self.cor[1])

        elif check == 2:
            self.automat_index += 1
            if self.waiting_for_stop:  # Конец движения, если переходим на ручное упр.
                self.waiting_for_stop = False
                self.paint.automat_flag = False
                return None

            self.automat_movement()  # Вызов функции автомат движения

    def on_change_man(self):  # Переход на шаги
        if self.waiting_for_stop:  # Ждем окончания анимации
            return None
        self.waiting_for_stop = True
        self.btn_step.show()

    def on_change_auto(self):
        if self.paint.automat_flag:
            return None
        self.btn_step.hide()
        self.paint.automat_flag = True
        self.automat_movement()  # Старт автомат. движения

    def automat_movement(self):  # Управление анимацией и коорд. автомат. движения
        if self.automat_index >= len(self.sc.coords):
            self.automat_index = 0
        self.cor = self.sc.automat_coord[self.sc.coords[self.automat_index]]  # Получение координат
        if self.cor[1] != self.paint.current_radius:
            self.paint.go_to_r_flag = True
        self.start_change_angle(self.cor[0], self.calculate_operation(self.paint.current_angle, self.cor[0]))  # Вызов
        # анимации

    def set_table_items(self):  # Заполнение таблицы
        points = self.sc.coords
        self.table.setRowCount(len(points))
        i = 0
        for point in points:
            angle = self.sc.automat_coord[point]  # Получение координат
            cord = self.sc.get_real_cor(angle[0] * self.sc.ONERAD, angle[1])
            self.table.setItem(i, 0, QTableWidgetItem(str(cord[0])))
            self.table.setItem(i, 1, QTableWidgetItem(str(cord[1])))
            i += 1


class WidgetControl(QWidget):  # Создание виджета, с контролирующими элементами
    def __init__(self):
        super().__init__()

        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox_rad = QHBoxLayout()
        hbox_angle = QHBoxLayout()

        self.btn = QPushButton("GoToAlpha")

        self.btn_r = QPushButton("GoToRadius")

        self.btn_r_one = QPushButton("Radius1")

        self.btn_r_two = QPushButton("Radius2")

        self.btn_a_plus = QPushButton("+45")

        self.btn_a_minus = QPushButton("-45")

        self.lineEd1 = QLineEdit(self)

        self.lineEd2 = QLineEdit(self)

        hbox_angle.addWidget(self.btn_a_plus)
        hbox_angle.addWidget(self.btn_a_minus)

        vbox1.addWidget(self.lineEd1)
        vbox1.addWidget(self.btn)
        vbox1.addLayout(hbox_angle)

        hbox_rad.addWidget(self.btn_r_one)
        hbox_rad.addWidget(self.btn_r_two)

        vbox2.addWidget(self.lineEd2)
        vbox2.addWidget(self.btn_r)
        vbox2.addLayout(hbox_rad)

        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)

        self.setLayout(hbox)


class MainWindow(QMainWindow):  # QMainWindow является главным виджетом всей программы
    def __init__(self, num=1, parent=None):
        super(MainWindow, self).__init__(parent)
        self.tab = QTabWidget()  # Инициализация экз. класса, использующийся для создания множества виджетов

        for i in range(num):
            i = str(i + 1)
            self.widget = WidgetSteps(i)  # Инициализ. указ. кол-ва виджетов и длбавление из в виджет вкладое
            self.tab.addTab(self.widget, i)

        self.setCentralWidget(self.tab)  # Установка главным виджетом в QMainWindow вкладок
        self.setWindowTitle("RobotPython")
        self.resize(500, 400)
        self.show()


if __name__ == "__main__":  # Проверка атрибута программы __name__
    # Если __main__ значит программа не является модулем, а главным компонентом
    import sys  # Импорт системного модуля sys нужного для запуска программы

    app = QApplication(sys.argv)  # Создание экз. класса и передача ему аргуметов командной строки
    window = MainWindow(num=1)  # Инициализация нашего главного виджета и передача ему кол-во вкладок
    sys.exit(app.exec_())  # Запуск перехватчтка событий

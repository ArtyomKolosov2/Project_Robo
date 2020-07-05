# -*- coding: utf-8 -*-
from math import sin, cos, pi, atan2, acos, sqrt


class Scara:
    scale = 1  # Масштаб
    hand = 0  # Хват руки ман. (левый или правый)
    a1 = 128 / scale  # Длинны кажого рычага
    a2 = 128 / scale
    a3 = 256.5 / scale
    R1 = 150.0 / scale  # Радиусы
    R2 = 280.0 / scale
    STEP_ANGLE = pi / 360 * 1.8
    NS = 20  # Кол-во импульса на 1 оборот
    VELOCITY = 1500  # Линейная скорость в мм/мин
    LENGTH = (a1 + a1 + a3) / scale  # Длинна всего манипулятора
    ONERAD = pi / 180  # Перевод в радианы
    ONEGRAD = 180 / pi  # Перевод в градусы
    automat_coord = {"1": (0, R1), "2": (45, R1), "3": (90, R1), "4": (135, R1),
                     "5": (180, R1), "6": (225, R1), "7": (270, R1), "8": (315, R1),
                     "11": (0, R2), "12": (45, R2), "13": (90, R2), "14": (135, R2),
                     "15": (180, R2), "16": (225, R2), "17": (270, R2), "18": (315, R2)
                     }  # Координаты для автомата

    def __init__(self, com):
        if com == "1":
            try:
                f = open("auto.cfg", "r")  # Взятие точек для автомата из файла
                self.coords = f.read().split(",")
                for i in range(len(self.coords)):  # Удаление лишних пробелов и символов перевода на новую строку
                    self.coords[i] = self.coords[i].strip()
                    self.coords[i] = self.coords[i].replace("\n", "")
                f.close()
            except FileNotFoundError:
                self.coords = ("1", "2", "3", "4", "14", "13", "12", "11", "8", "7", "6", "5", "15", "16", "17", "18")

        elif com == "2":
            self.coords = ("1", "2", "3", "4", "14", "13", "12", "11", "8", "7", "6", "5", "15", "16", "17", "18")

    @staticmethod
    def get_real_cor(angle, radius, offset_x=0, offset_y=0):  # Получение координат в полярной системе
        return (round(radius * cos(angle) + offset_x, 2),
                round(radius * sin(angle) + offset_y, 2))

    @staticmethod
    def calculate_angle(x, y, offset_x=0, offset_y=0):  # Высчитываем угол для inverse_problem
        return round(atan2(y - offset_y, x - offset_x), 3)

    @staticmethod
    def theory_of_cos(a1, a2, a3):  # Теорема косинусов
        try:
            fi = round(acos((a1 ** 2 + a2 ** 2 - a3 ** 2) / (2 * a1 * a2)), 2)
        except ValueError:
            a1 += 1
            fi = round(acos((a1 ** 2 + a2 ** 2 - a3 ** 2) / (2 * a1 * a2)), 2)
        except ZeroDivisionError:
            a1 -= 1
            fi = round(acos((a1 ** 2 + a2 ** 2 - a3 ** 2) / (2 * a1 * a2)), 2)
        return fi

    @staticmethod
    def length(x, y, x1, y1):  # Высчитывание длинны по точкам начала и конца
        return round(sqrt(pow(x - x1, 2) +
                          pow(y - y1, 2)), 4)

    @staticmethod
    def round_2(x):
        return round(x, 2)

    def inverse_problem(self, stripe, x=0, y=0, angle=0, hand=0):  # Решение обратной проблемы
        if not angle and (x and y):
            angle = self.calculate_angle(x, y)
        beta = self.theory_of_cos(stripe, self.a1, self.a2)
        if not hand:
            fi1 = angle - beta
        else:
            fi1 = angle + beta
        return fi1


class Case:  # Класс содержащий описание контейнеров.
    max_circle = 20
    circle_pos = [0 for i in range(max_circle)]

    def __init__(self, indexes):
        self.indexes = list(map(int, indexes.split(".")))
        for i in self.indexes:
            if 0 <= i < self.max_circle + 1:
                self.circle_pos[i - 1] = 1
        self.circle = self.circle_pos.count(1)

    def count_parts(self, sym=1):
        return self.circle_pos.count(sym)

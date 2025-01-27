import json
from PyQt5 import QtWidgets
import math

class SacredAlgorithm:
    """
    Основной класс для работы с уникальными алгоритмами обработки графов.
    """

    def __init__(self):
        self.t_iterations = None  # Количество итераций
        self.alpha = None  # Специальный коэффициент
        self.matrix = None  # Матрица смежности
        self.list_from_edges = []  # Список рёбер

    @staticmethod
    def sacred_algorithm_calling():
        """
        Основной метод для запуска алгоритмов. Связывается с кнопкой.

        :return: None
        """
        # Запрос количества итераций у пользователя
        t_iterations, ok = QtWidgets.QInputDialog.getInt(
            None, "Количество итераций", "Введите количество итераций:", 10, 1, 100000, 1
        )
        if not ok:
            return

        # Запрос коэффициента alpha у пользователя
        alpha, ok = QtWidgets.QInputDialog.getDouble(
            None, "Коэффициент alpha", "Введите значение коэффициента alpha:", 1.0, 0.0, 100.0, 2
        )
        if not ok:
            return

        # Сохраняем значения в соответствующие поля
        algorithm = SacredAlgorithm()
        algorithm.t_iterations = t_iterations
        algorithm.alpha = alpha

        # Запрос файла с матрицей смежности
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Выберите файл с матрицей смежности", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Файл не выбран.")
            return

        try:
            # Загрузка матрицы из файла
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            matrix = data.get("adjacency_matrix")
            if not matrix:
                raise ValueError("Матрица смежности отсутствует в файле.")

            # Сохраняем матрицу в поле класса
            algorithm.matrix = matrix

            # Проверяем матрицу на корректность
            SacredAlgorithm.validate_adjacency_matrix(matrix)

            # Преобразуем матрицу смежности в список рёбер
            algorithm.list_from_edges = SacredAlgorithm.adjacency_matrix_to_edges(matrix)

        except (json.JSONDecodeError, ValueError) as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Возникла ошибка при загрузке матрицы: {e}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Непредвиденная ошибка: {e}")

    @staticmethod
    def validate_adjacency_matrix(matrix):
        """
        Проверяет матрицу смежности на корректность.

        :return: None. Уведомляет пользователя через окно сообщений PyQt.
        """
        size = len(matrix)

        for i in range(size):
            for j in range(size):
                # Проверка на None перед math.isnan
                if matrix[i][j] is None or matrix[j][i] is None:
                    continue

                # Если элемент равен NaN, пропускаем проверку
                if isinstance(matrix[i][j], float) and math.isnan(matrix[i][j]):
                    continue

                # Проверка главной диагонали
                if i == j:
                    if matrix[i][j] is None:
                        raise ValueError(f"Ошибка: элемент на главной диагонали matrix[{i}][{j}] отсутствует.")
                    if matrix[i][j] != 0:
                        raise ValueError(f"Ошибка: элемент на главной диагонали matrix[{i}][{j}] должен быть 0.")

                # Проверка симметричности
                if matrix[i][j] != matrix[j][i]:
                    if matrix[i][j] is not None and matrix[j][i] is not None:
                        raise ValueError(f"Ошибка: матрица не симметрична на позициях [{i}][{j}] и [{j}][{i}].")

                # Проверка на неотрицательность
                if matrix[i][j] is not None and matrix[i][j] < 0:
                    raise ValueError(f"Ошибка: отрицательное значение matrix[{i}][{j}]={matrix[i][j]}. Элементы должны быть >= 0.")

        QtWidgets.QMessageBox.information(None, "Успех", "Матрица корректна.")

    @staticmethod
    def adjacency_matrix_to_edges(matrix):
        """
        Преобразует матрицу смежности в список рёбер.

        :param matrix: Матрица смежности.
        :return: Список рёбер.
        """
        edges = []
        size = len(matrix)

        for i in range(size):
            for j in range(i + 1, size):  # Чтобы не добавлять одно и то же ребро дважды
                if matrix[i][j] is None or isinstance(matrix[i][j], float) and math.isnan(matrix[i][j]):
                    continue  # Пропускаем отсутствующие рёбра (None или NaN)

                # Добавляем ребро, если оно существует
                edge = {
                    "start": i + 1,  # Нумерация вершин с 1
                    "end": j + 1,
                    "weight": matrix[i][j]
                }
                edges.append(edge)

        return edges

import json
from PyQt5 import QtWidgets
from Core.graph import Graph, Vertex, Edge
import math
from Core.vizualization import Canvas
import random

class SacredAlgorithm:
    def __init__(self, canvas):
        self.t_iterations = None  # Количество итераций
        self.alpha = None  # Специальный коэффициент
        self.matrix = None  # Матрица смежности
        self.list_from_edges = []  # Список рёбер
        self.d_evklid = []  # Массив евклидовых расстояний между вершинами
        self.d = []  # Массив теоретических расстояний между вершинами
        self.i_previous = []  # Массив координат вершин на предыдущей итерации
        self.i_current = []  # Массив координат вершин на текущей итерации
        self.error = []  # Массив хранящий ошибки для каждой итерации
        self.scale_screen = []  # Массив, хранящий координаты точек для отображения на холсте
        self.canvas_width = None  
        self.canvas_height = None  
        self.graph = Graph()
        self.canvas = canvas

    def set_canvas_dimensions(self):
        """Устанавливаем размеры холста для использования в алгоритме"""
        if self.canvas is None:
            raise ValueError("Объект Canvas не может быть None.")
        
        # Получаем размеры холста из объекта Canvas
        width, height = self.canvas.get_canvas_size()  
        
        # Проверяем, что размеры корректны
        if width <= 0 or height <= 0:
            raise ValueError(f"Невозможные размеры холста: ширина = {width}, высота = {height}")
        
        # Устанавливаем размеры холста
        self.canvas_width = width
        self.canvas_height = height
        
        # Выводим обновленные размеры
        print(f"Размеры холста обновлены: Ширина = {self.canvas_width}, Высота = {self.canvas_height}")

        
    def sacred_algorithm_calling(self):      
        self.set_canvas_dimensions()
        t_iterations, ok = QtWidgets.QInputDialog.getInt(
            None, "Количество итераций", "Введите количество итераций:", 10, 1, 100000, 1
        )
        if not ok:
            return

        alpha, ok = QtWidgets.QInputDialog.getDouble(
            None, "Коэффициент alpha", "Введите значение коэффициента alpha:", 1.0, 0.0, 100.0, 2
        )
        if not ok:
            return

        self.t_iterations = t_iterations
        self.alpha = alpha

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Выберите файл с матрицей смежности", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Файл не выбран.")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            matrix = data.get("adjacency_matrix")
            if not matrix:
                raise ValueError("Матрица смежности отсутствует в файле.")

            self.matrix = matrix
            SacredAlgorithm.validate_adjacency_matrix(matrix)
            self.list_from_edges = SacredAlgorithm.adjacency_matrix_to_edges(matrix)

        except (json.JSONDecodeError, ValueError) as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Возникла ошибка при загрузке матрицы: {e}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Непредвиденная ошибка: {e}")
        
        self.convert_edges_to_theoretical_distances()
        self.randomize_vertex_positions()

    def validate_adjacency_matrix(matrix):
        size = len(matrix)
        for i in range(size):
            for j in range(size):
                if matrix[i][j] is None or matrix[j][i] is None:
                    continue

                if isinstance(matrix[i][j], float) and math.isnan(matrix[i][j]):
                    continue

                if i == j:
                    if matrix[i][j] is None:
                        raise ValueError(f"Ошибка: элемент на главной диагонали matrix[{i}][{j}] отсутствует.")
                    if matrix[i][j] != 0:
                        raise ValueError(f"Ошибка: элемент на главной диагонали matrix[{i}][{j}] должен быть 0.")

                if matrix[i][j] != matrix[j][i]:
                    if matrix[i][j] is not None and matrix[j][i] is not None:
                        raise ValueError(f"Ошибка: матрица не симметрична на позициях [{i}][{j}] и [{j}][{i}].")

                if matrix[i][j] is not None and matrix[i][j] < 0:
                    raise ValueError(f"Ошибка: отрицательное значение matrix[{i}][{j}]={matrix[i][j]}. Элементы должны быть >= 0.")

        QtWidgets.QMessageBox.information(None, "Успех", "Матрица корректна.")

    def adjacency_matrix_to_edges(matrix):
        edges = []
        size = len(matrix)
        for i in range(size):
            for j in range(i + 1, size):  
                if matrix[i][j] is None or isinstance(matrix[i][j], float) and math.isnan(matrix[i][j]):
                    continue 

                edge = {
                    "start": i + 1, 
                    "end": j + 1,
                    "weight": matrix[i][j]
                }
                edges.append(edge)

        return edges

    def convert_edges_to_theoretical_distances(self):
        self.d = [(edge["start"], edge["end"], edge["weight"]) for edge in self.list_from_edges]
        print("Массив теоретических расстояний (начальная вершина, конечная вершина, вес):")
        for item in self.d:
            print(item)
        print(f"Размеры холста обновлены: Ширина = {self.canvas_width}, Высота = {self.canvas_height}")

    def randomize_vertex_positions(self):
        # Проверка на корректность размеров холста
        if self.canvas_width is None or self.canvas_height is None:
            raise ValueError(f"Размеры холста не установлены: ширина = {self.canvas_width}, высота = {self.canvas_height}")

        # Очистка массива координат
        self.i_previous = []

        # Проходим по всем вершинам (извлекаем номера вершин из матрицы)
        for i in range(len(self.matrix)):
            # Генерируем случайные координаты для каждой вершины
            random_x = random.randint(0, self.canvas_width)
            random_y = random.randint(0, self.canvas_height)
            
            # Записываем номер вершины и её координаты в self.i_previous
            self.i_previous.append((i + 1, random_x, random_y))  # Нумерация с 1, поэтому i+1
            vertex = self.graph.vertices.get(i + 1)

            # Если вершина не найдена, создаем новую
            if not vertex:
                vertex = Vertex(i + 1, x=random_x, y=random_y)
                self.graph.add_vertex(vertex)

            # Обновляем координаты вершины
            vertex.x = random_x
            vertex.y = random_y

            # Выводим координаты в консоль для проверки
            print(f"Вершина {i + 1} размещена на координатах ({random_x}, {random_y})")


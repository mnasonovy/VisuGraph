import json
from PyQt5 import QtWidgets
from Core.graph import Graph, Vertex, Edge
import math
from Core.vizualization import Canvas
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
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
        
        width, height = self.canvas.get_canvas_size()  
        
        if width <= 0 or height <= 0:
            raise ValueError(f"Невозможные размеры холста: ширина = {width}, высота = {height}")

        self.canvas_width = width
        self.canvas_height = height
  
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
        self.scale_vertices_to_canvas()
        self.draw_vertices_from_scaled_data()
        self.calculate_euclidean_distances()

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

    def calculate_euclidean_distances(self):
        """Вычисляет евклидовы расстояния между всеми парами вершин и сохраняет их в self.d_evklid."""
        self.d_evklid = []  
        for i in range(len(self.scale_screen)):
            for j in range(i + 1, len(self.scale_screen)):  
                vertex_id_1, x1, y1 = self.scale_screen[i]
                vertex_id_2, x2, y2 = self.scale_screen[j]

                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                self.d_evklid.append((vertex_id_1, vertex_id_2, distance))
                print(f"Евклидово расстояние между вершинами {vertex_id_1} и {vertex_id_2}: {distance:.2f}")


    def randomize_vertex_positions(self):
        if self.canvas_width is None or self.canvas_height is None:
            raise ValueError(f"Размеры холста не установлены: ширина = {self.canvas_width}, высота = {self.canvas_height}")
        self.i_previous = []
        for i in range(len(self.matrix)):
            random_x = random.randint(0, self.canvas_width)
            random_y = random.randint(0, self.canvas_height)
            self.i_previous.append((i + 1, random_x, random_y)) 
            vertex = self.graph.vertices.get(i + 1)
            if not vertex:
                vertex = Vertex(i + 1, x=random_x, y=random_y)
                self.graph.add_vertex(vertex)
            vertex.x = random_x
            vertex.y = random_y
            print(f"Вершина {i + 1} размещена на координатах ({random_x}, {random_y})")


    def scale_vertices_to_canvas(self):
        """Масштабирует координаты вершин, чтобы они соответствовали размеру холста."""
        if not self.i_previous:
            raise ValueError("Список i_previous пуст. Убедитесь, что вершины были случайным образом размещены.")
        min_x = min(self.i_previous, key=lambda v: v[1])[1]
        max_x = max(self.i_previous, key=lambda v: v[1])[1]
        min_y = min(self.i_previous, key=lambda v: v[2])[2]
        max_y = max(self.i_previous, key=lambda v: v[2])[2]

        print(f"Мин. и макс. координаты по X: ({min_x}, {max_x})")
        print(f"Мин. и макс. координаты по Y: ({min_y}, {max_y})")

        scale_x = self.canvas_width / (max_x - min_x) if max_x != min_x else 1
        scale_y = self.canvas_height / (max_y - min_y) if max_y != min_y else 1

        self.scale_screen = []  
        for i, x, y in self.i_previous:
            vertex = self.graph.vertices.get(i)
            if vertex:
                scaled_x = (x - min_x) * scale_x
                scaled_y = (y - min_y) * scale_y
                vertex.x = scaled_x
                vertex.y = scaled_y
                self.scale_screen.append((i, scaled_x, scaled_y))

        print(f"Коэффициенты масштаба: X={scale_x}, Y={scale_y}")


    def draw_vertices_from_scaled_data(self):
        """Отрисовывает вершины на холсте из данных в self.scale_screen."""
        for vertex_id, scaled_x, scaled_y in self.scale_screen:
            vertex = self.graph.vertices.get(vertex_id)
            if vertex:
                self.canvas.create_vertex(QPointF(scaled_x, scaled_y))

import json
import math
import random
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem

from Core.graph import Graph, Vertex, Edge
from Core.vizualization import Canvas

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
        self.timer = QTimer()  
        self.timer.timeout.connect(self.on_iteration)  

        self.current_iteration = 0

    def set_canvas_dimensions(self):
        """Устанавливаем размеры холста для использования в алгоритме"""
        if self.canvas is None:
            raise ValueError("Объект Canvas не может быть None.")
        
        width, height = self.canvas.get_canvas_size()  
        
        if width <= 0 or height <= 0:
            raise ValueError(f"Невозможные размеры холста: ширина = {width}, высота = {height}")

        self.canvas_width = round(width*0.9)
        self.canvas_height = round(height*0.9)

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
        self.calculate_euclidean_distances()
        self.calculate_error()
        self.scale_vertices_to_canvas()
        self.draw_vertices_and_edges_from_scaled_data()
        self.update_vertex_positions()

        self.current_iteration = 1  
        self.timer.start(100) 
        self.on_iteration() 

    def on_iteration(self):
        """Обработчик итерации, вызываемый по таймеру"""
        if self.current_iteration <= self.t_iterations:
            self.i_previous = self.i_current  
            self.calculate_euclidean_distances()  
            self.calculate_error()  
            self.scale_vertices_to_canvas()  
            self.clear_canvas_and_graph()  
            self.draw_vertices_and_edges_from_scaled_data()  
            self.update_vertex_positions()  
            self.current_iteration += 1  
        else:
            self.timer.stop()  

            self.i_previous = self.i_current  
            self.scale_vertices_to_canvas()  
            self.calculate_euclidean_distances()  
            self.clear_canvas_and_graph() 
            self.draw_vertices_and_edges_from_scaled_data()  
            self.plot_error_graph()

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

    def calculate_euclidean_distances(self):
        """Вычисляет евклидовы расстояния между всеми парами вершин из self.i_previous и сохраняет их в self.d_evklid."""
        self.d_evklid = [] 
        for i in range(len(self.i_previous)):
            for j in range(i + 1, len(self.i_previous)):  
                vertex_id_1, x1, y1 = self.i_previous[i]
                vertex_id_2, x2, y2 = self.i_previous[j]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                self.d_evklid.append((vertex_id_1, vertex_id_2, distance))

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

    def scale_vertices_to_canvas(self):
        """Масштабирует координаты вершин, чтобы они соответствовали размеру холста."""
        if not self.i_previous:
            raise ValueError("Список i_previous пуст. Убедитесь, что вершины были случайным образом размещены.")
        min_x = min(self.i_previous, key=lambda v: v[1])[1]
        max_x = max(self.i_previous, key=lambda v: v[1])[1]
        min_y = min(self.i_previous, key=lambda v: v[2])[2]
        max_y = max(self.i_previous, key=lambda v: v[2])[2]
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



    def draw_vertices_and_edges_from_scaled_data(self):
        """Отрисовывает вершины и рёбра на холсте из данных в self.scale_screen и self.d_evklid."""
        for vertex_id, scaled_x, scaled_y in self.scale_screen:
            vertex = Vertex(vertex_id, x=scaled_x, y=scaled_y)
            self.graph.add_vertex(vertex)  
            self.canvas.create_vertex(QPointF(scaled_x, scaled_y))  

        for start_id, end_id, weight in self.d_evklid:
            start_vertex = self.graph.vertices.get(start_id)
            end_vertex = self.graph.vertices.get(end_id)

            if start_vertex and end_vertex:
                weight = round(weight)
                self.canvas.create_edge_special(start_id, end_id, weight) 
        self.canvas.update()  
        self.scale_screen = []  


    def clear_canvas_and_graph(self):
        """Очистить холст и граф от старых данных (вершин и рёбер)."""
        self.canvas.scene.clear() 
        self.canvas.graph.vertices.clear()  
        self.canvas.graph.edges.clear()  
        self.canvas.update()  

    def calculate_error(self):
        """Вычисляет ошибку по формуле sum по i,j i>j (dij - dij_evklid)^2 и сохраняет её в self.error."""
        euclidean_distances = { (min(start, end), max(start, end)): dist for start, end, dist in self.d_evklid }
        total_error = 0
        for start, end, dij in self.d:  
            if (min(start, end), max(start, end)) not in euclidean_distances:
                continue
            dij_evklid = euclidean_distances[(min(start, end), max(start, end))]
            error_term = (dij - dij_evklid) ** 2
            total_error += error_term
        self.error.append(total_error)

    def plot_error_graph(self):
        """Функция для построения графика зависимости ошибки от номера итерации"""
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, len(self.error) + 1), self.error, marker='o', color='b', linestyle='-', markersize=5)
        plt.title('Зависимость ошибки от номера итерации')
        plt.xlabel('Номер итерации')
        plt.ylabel('Ошибка')
        plt.grid(True)
        plt.show()

    def update_vertex_positions(self):
        """Вычисляет улучшенные координаты для каждой вершины по заданной формуле."""
        self.i_current = []
        for i, (vertex_id_i, x_i_prev, y_i_prev) in enumerate(self.i_previous):
            vertex_i = self.graph.vertices.get(vertex_id_i)
            if not vertex_i:
                continue  
            x_i_current = x_i_prev
            y_i_current = y_i_prev
            for j, (vertex_id_j, x_j_prev, y_j_prev) in enumerate(self.i_previous):
                if i == j:
                    continue 

                vertex_j = self.graph.vertices.get(vertex_id_j)
                if not vertex_j:
                    continue  

                dij = None
                for edge in self.d:
                    if (edge[0] == vertex_id_i and edge[1] == vertex_id_j) or (edge[0] == vertex_id_j and edge[1] == vertex_id_i):
                        dij = edge[2]
                        break

                if dij is None:
                    continue 

                dij_evklid = None
                for start, end, dist in self.d_evklid:
                    if (start == vertex_id_i and end == vertex_id_j) or (start == vertex_id_j and end == vertex_id_i):
                        dij_evklid = dist
                        break

                if dij_evklid is None:
                    continue  

                factor = (dij - dij_evklid) / dij_evklid
                dx = x_i_prev - x_j_prev
                dy = y_i_prev - y_j_prev

                x_i_current += self.alpha * factor * dx
                y_i_current += self.alpha * factor * dy

            if vertex_i:
                vertex_i.x = x_i_current
                vertex_i.y = y_i_current
            
            self.i_current.append((vertex_id_i, x_i_current, y_i_current))





from PyQt5 import QtWidgets
import json
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QGraphicsLineItem, QMessageBox
from PyQt5.QtCore import QPointF
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas
from GUI.functionals.work_window_functional import WorkWindowFunctional


def create_graph_from_edge_list(canvas, functional_instance, file_path=None):
    """
    Создаёт граф на основе списка рёбер, загруженного из файла JSON.
    Файл должен быть в следующем формате:
    {
        "edges": [
            {"start": 1, "end": 2, "weight": 5},
            {"start": 1, "end": 3, "weight": 3},
            {"start": 2, "end": 3, "weight": 1},
            {"start": 3, "end": 4, "weight": 2}
        ]
    }
    """
    functional_instance.clear_graph()  # Очищаем текущий граф

    # Если файл не передан, откроем диалог для выбора файла
    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  # Если файл не выбран, выходим из функции

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        for edge in data.get("edges", []):
            start = edge.get("start")
            end = edge.get("end")
            weight = edge.get("weight", 1)  # Извлекаем вес рёбер

            if start is None or end is None:
                QMessageBox.warning(None, "Ошибка", f"Некорректный формат JSON: {edge}")
                continue

            # Создаем вершины, если их ещё нет
            if start not in canvas.graph.vertices:
                vertex_start = Vertex(start, x=100 + start * 10, y=100)
                canvas.graph.add_vertex(vertex_start)  # Добавляем вершину в граф
                canvas.create_vertex_visual(vertex_start)  # Визуализируем вершину
            if end not in canvas.graph.vertices:
                vertex_end = Vertex(end, x=100 + end * 10, y=200)
                canvas.graph.add_vertex(vertex_end)  # Добавляем вершину в граф
                canvas.create_vertex_visual(vertex_end)  # Визуализируем вершину

            # Теперь передаем вес рёбер, который есть в файле, в метод create_edge_special
            canvas.create_edge_special(start, end, weight)  # Передаем start_id, end_id и вес рёбер

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")


def create_graph_from_adjacency_matrix(canvas, functional_instance):
    """
    Создаёт граф на основе матрицы смежности, загруженной из файла.
    """
    functional_instance.clear_graph()  # Очищаем текущий граф

    file_path, _ = QFileDialog.getOpenFileName(None, "Загрузить JSON файл", "", "JSON Files (*.json);;All Files (*)")
    if not file_path:
        return

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        adjacency_matrix = data.get("adjacency_matrix", [])
        if not adjacency_matrix:
            QMessageBox.warning(None, "Ошибка", "Матрица смежности отсутствует.")
            return

        # Создаем вершины
        for i in range(len(adjacency_matrix)):
            vertex_id = i + 1  # ID вершин начинаются с 1
            if vertex_id not in canvas.graph.vertices:  # Проверка на существование вершины
                vertex = Vertex(vertex_id, x=100 + i * 50, y=100)
                canvas.graph.add_vertex(vertex)  # Добавляем вершину в граф
                canvas.create_vertex_visual(vertex)  # Визуализируем вершину

        # Создаем рёбра
        for i, row in enumerate(adjacency_matrix):
            for j, value in enumerate(row):
                if value != 0:
                    edge_obj = Edge(
                        canvas.graph.vertices[i + 1],  # Обновляем индексы
                        canvas.graph.vertices[j + 1],  # Обновляем индексы
                        weight=value
                    )
                    canvas.graph.add_edge(canvas.graph.vertices[i + 1], canvas.graph.vertices[j + 1], value)  # Используем add_edge
                    canvas.create_edge_special(i + 1, j + 1, value)  # Используем новую функцию для создания рёбер

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")


def create_graph_from_incidence_matrix(canvas, functional_instance, file_path=None):
    """
    Создаёт граф на основе матрицы инцидентности, загруженной из файла.
    """
    functional_instance.clear_graph()  # Очищаем текущий граф

    # Если файл не передан, откроем диалог для выбора файла
    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  # Если файл не выбран, выходим из функции

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        incidence_matrix = data.get("incidence_matrix", [])
        if not incidence_matrix:
            QMessageBox.warning(None, "Ошибка", "Матрица инцидентности отсутствует.")
            return

        weights = data.get("weights", {})

        # Создаем вершины
        for i in range(len(incidence_matrix)):
            vertex_id = i + 1  # Нумерация вершин начинается с 1
            if vertex_id not in canvas.graph.vertices:  # Проверка на существование вершины
                vertex = Vertex(vertex_id, x=100 + i * 50, y=100)  # Вершины начинаются с 1
                canvas.graph.add_vertex(vertex)  # Добавляем вершину в граф
                canvas.create_vertex_visual(vertex)  # Визуализируем вершину

        # Создаем рёбра
        for j, column in enumerate(zip(*incidence_matrix)):  # Столбцы матрицы инцидентности
            nodes = [i + 1 for i, value in enumerate(column) if value != 0]  # Находим вершины, инцидентные ребру

            if len(nodes) != 2:
                QMessageBox.warning(None, "Ошибка", f"Некорректная колонка {j} в матрице инцидентности.")
                continue

            # Первая единица - это начальная вершина, вторая единица - конечная вершина
            start, end = nodes[0], nodes[1]  # Вершины начинаются с 1

            # Получаем вес рёбра из файла
            weight = weights.get(str(j), 1)  # Если вес не найден, ставим 1 по умолчанию

            # Создаём ребро и добавляем его в граф
            canvas.create_edge_special(start, end, weight)

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")



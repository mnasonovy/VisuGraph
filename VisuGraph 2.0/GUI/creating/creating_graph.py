from PyQt5 import QtWidgets
import json
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QGraphicsLineItem, QMessageBox
from PyQt5.QtCore import QPointF
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas
from GUI.functionals.work_window_functional import WorkWindowFunctional


def create_graph_from_edge_list(canvas, functional_instance, file_path=None):
    functional_instance.clear_graph()  

    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        for edge in data.get("edges", []):
            start = edge.get("start")
            end = edge.get("end")
            weight = edge.get("weight", 1) 

            if start is None or end is None:
                QMessageBox.warning(None, "Ошибка", f"Некорректный формат JSON: {edge}")
                continue

            if start not in canvas.graph.vertices:
                vertex_start = Vertex(start, x=100 + start * 10, y=100)
                canvas.graph.add_vertex(vertex_start) 
                canvas.create_vertex_visual(vertex_start)  
            if end not in canvas.graph.vertices:
                vertex_end = Vertex(end, x=100 + end * 10, y=200)
                canvas.graph.add_vertex(vertex_end) 
                canvas.create_vertex_visual(vertex_end)  

            canvas.create_edge_special(start, end, weight)  

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")


def create_graph_from_adjacency_matrix(canvas, functional_instance, file_path=None):
    """
    Создаёт граф на основе матрицы смежности, загруженной из файла JSON.
    Строки и колонки матрицы - это номера вершин (начиная с 1), а значения - веса рёбер.
    """
    functional_instance.clear_graph()  

    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        adjacency_matrix = data.get("adjacency_matrix", [])
        if not adjacency_matrix:
            QMessageBox.warning(None, "Ошибка", "Матрица смежности отсутствует.")
            return

        for i in range(len(adjacency_matrix)):
            vertex_id = i + 1 
            if vertex_id not in canvas.graph.vertices:  
                vertex = Vertex(vertex_id, x=100 + i * 50, y=100)
                canvas.graph.add_vertex(vertex) 
                canvas.create_vertex_visual(vertex)  

        for i, row in enumerate(adjacency_matrix):
            for j, value in enumerate(row):
                if value != 0:
                    start_id = i + 1  
                    end_id = j + 1  
                    weight = value  

                    canvas.create_edge_special(start_id, end_id, weight)  

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")

def create_graph_from_incidence_matrix(canvas, functional_instance, file_path=None):
    """
    Создаёт граф на основе матрицы инцидентности, загруженной из файла.
    """
    functional_instance.clear_graph()  

    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        incidence_matrix = data.get("incidence_matrix", [])
        if not incidence_matrix:
            QMessageBox.warning(None, "Ошибка", "Матрица инцидентности отсутствует.")
            return

        weights = data.get("weights", {})

        for i in range(len(incidence_matrix)):
            vertex_id = i + 1 
            if vertex_id not in canvas.graph.vertices:  
                vertex = Vertex(vertex_id, x=100 + i * 50, y=100)  
                canvas.graph.add_vertex(vertex)  
                canvas.create_vertex_visual(vertex)  

        for j, column in enumerate(zip(*incidence_matrix)):  
            nodes = [i + 1 for i, value in enumerate(column) if value != 0]  

            if len(nodes) != 2:
                QMessageBox.warning(None, "Ошибка", f"Некорректная колонка {j} в матрице инцидентности.")
                continue
            start, end = nodes[0], nodes[1]  
            weight = weights.get(str(j), 1)  
            canvas.create_edge_special(start, end, weight)

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")



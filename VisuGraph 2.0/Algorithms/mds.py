from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas
import json
import random
import numpy as np
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt

# Функция для загрузки и проверки матрицы смежности
def load_and_validate_adjacency_matrix():
    """Загружает матрицу смежности и выполняет её проверку."""
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Выберите JSON файл", "", "JSON Files (*.json);;All Files (*)"
    )
    if not file_path:
        return None  # Если файл не выбран, выходим

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        adjacency_matrix = data.get("adjacency_matrix", [])
        if not adjacency_matrix:
            QMessageBox.warning(None, "Ошибка", "Матрица смежности отсутствует.")
            return None

        # Проверяем матрицу на условия
        if not is_valid_adjacency_matrix(adjacency_matrix):
            return None  # Если матрица некорректна, возвращаем None

        return adjacency_matrix  # Возвращаем валидную матрицу смежности

    except (json.JSONDecodeError, IOError):
        QMessageBox.critical(None, "Ошибка", "Не удалось загрузить файл JSON.")
        return None

# Проверка корректности матрицы смежности
def is_valid_adjacency_matrix(matrix):
    """Проверка, что матрица смежности симметрична и что все элементы на главной диагонали равны 0"""
    n = len(matrix)
    for i in range(n):
        if matrix[i][i] != 0:  # Элементы на главной диагонали должны быть 0
            QMessageBox.warning(None, "Ошибка", f"Элемент на главной диагонали ({i}, {i}) не равен 0!")
            return False
        for j in range(i + 1, n):  # Проверка симметричности
            if matrix[i][j] != matrix[j][i]:
                QMessageBox.warning(None, "Ошибка", f"Матрица не симметрична на позиции ({i}, {j}) и ({j}, {i})!")
                return False
            if matrix[i][j] <= 0:
                QMessageBox.warning(None, "Ошибка", f"Элемент матрицы смежности ({i}, {j}) должен быть больше 0!")
                return False
    return True

# Функция для начального случайного размещения вершин
def initial_random_placement(vertices, canvas):
    """Функция для начального случайного размещения вершин."""
    canvas_width, canvas_height = 1500, 800  # Размеры канваса

    for vertex in vertices:
        vertex.x = random.randint(50, canvas_width - 50)
        vertex.y = random.randint(50, canvas_height - 50)
        
        # Добавляем вершину в граф
        canvas.graph.add_vertex(vertex)
        canvas.create_vertex_visual(vertex)

# Функция для вычисления энергии системы на текущей итерации
def compute_energy(D, vertices):
    """
    Вычисляет энергию системы на текущей итерации.
    :param D: Матрица расстояний (NxN).
    :param vertices: Список объектов класса Vertex.
    :return: Энергия системы на текущей итерации.
    """
    n = len(D)
    energy = 0.0
    
    for i in range(n):
        for j in range(i + 1, n):
            dij = D[i][j]  # Вес ребра
            dist_ij = np.linalg.norm([vertices[i].x - vertices[j].x, vertices[i].y - vertices[j].y])  # Евклидово расстояние

            energy += (dij - dist_ij) ** 2
    
    return energy


def minimize_energy(vertices, D, canvas, alpha, tolerance=1e-5, interval=500):
    """Минимизирует энергию, двигая вершины и обновляя холст.""" 
    error_history = []  # История ошибок для отображения графика

    def iteration_step(iteration):
        """Шаг итерации алгоритма минимизации энергии"""
        energy = compute_energy(D, vertices)
        error_history.append(energy)

        print(f"Iteration {iteration}: Energy = {energy}")

        # Двигаем вершины на основе минимизации энергии
        prev_energy = energy
        for i, vertex in enumerate(vertices):
            grad_x = 0
            grad_y = 0
            for j, other_vertex in enumerate(vertices):
                if i != j:
                    dij = D[i][j]
                    dist_ij = np.linalg.norm([vertex.x - other_vertex.x, vertex.y - other_vertex.y])
                    grad_x += (dij - dist_ij) * (vertex.x - other_vertex.x) / dist_ij
                    grad_y += (dij - dist_ij) * (vertex.y - other_vertex.y) / dist_ij

            vertex.x -= alpha * grad_x  # Шаг по антиградиенту
            vertex.y -= alpha * grad_y  # Шаг по антиградиенту
            vertex.item.setPos(vertex.x, vertex.y)

        canvas.update()

        # Если изменение энергии стало очень маленьким, останавливаем итерации
        if abs(prev_energy - energy) < tolerance:
            timer.stop()
            print(f"Алгоритм завершен на итерации {iteration} с минимальной энергией.")
            plt.plot(range(1, len(error_history) + 1), error_history)
            plt.xlabel('Iteration')
            plt.ylabel('Energy')
            plt.title('Energy Minimization')
            plt.show()

    # Создаем таймер, который будет выполнять итерации каждую секунду
    timer = QTimer()
    timer.timeout.connect(lambda: iteration_step(len(error_history) + 1))
    timer.start(interval)

    iteration_step(0)


def run_multidimensional_scaling(canvas):
    """Запуск алгоритма многомерного шкалирования"""
    adjacency_matrix = load_and_validate_adjacency_matrix()
    
    if adjacency_matrix is not None:
        QMessageBox.information(None, "Успех", "Матрица смежности загружена и проверена успешно!")

        alpha, ok = QInputDialog.getDouble(None, "Коэффициент альфа", "Введите коэффициент альфа:", 1.0, 0.0, 10.0, 2)

        if ok:
            vertices = []
            for i in range(len(adjacency_matrix)):
                vertex = Vertex(i, canvas=canvas)  # Передаем canvas в вершину
                vertices.append(vertex)

            D = adjacency_matrix

            initial_random_placement(vertices, canvas) 

            minimize_energy(vertices, D, canvas, alpha)
        else:
            print("Операция отменена.")
    else:
        print("Ошибка при загрузке матрицы смежности.")

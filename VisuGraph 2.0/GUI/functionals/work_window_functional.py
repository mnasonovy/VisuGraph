from PyQt5 import QtWidgets
import json
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import QPointF
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas

class WorkWindowFunctional:
    def __init__(self, main_window, ui, canvas):
        self.main_window = main_window
        self.ui = ui
        self.canvas = canvas  # Передаем ссылку на Canvas

        # Подключение кнопок меню к методам
        self.ui.return_to_menu_action.triggered.connect(self.return_to_start_window)
        self.ui.save_graph_action.triggered.connect(self.save_graph)
        self.ui.load_graph_action.triggered.connect(self.load_graph)
        self.ui.clear_graph_action.triggered.connect(self.clear_graph)
        self.ui.graph_changing_mode_action.toggled.connect(self.toggle_graph_changing_mode)

        # Подключение действий меню "Алгоритмы"
        self.ui.bfs_action.triggered.connect(self.run_bfs)
        self.ui.dfs_action.triggered.connect(self.run_dfs)
        self.ui.dijkstra_action.triggered.connect(self.run_dijkstra)
        self.ui.prim_action.triggered.connect(self.run_prim)

        # Подключение действий меню "Создать граф"
        self.ui.adjacency_matrix_action.triggered.connect(self.create_from_adjacency_matrix)
        self.ui.incidence_matrix_action.triggered.connect(self.create_from_incidence_matrix)
        self.ui.edge_list_action.triggered.connect(self.create_from_edge_list)

    def return_to_start_window(self):
        """Возвращает пользователя в стартовое окно."""
        from GUI.functionals.start_window_functional import StartWindowFunctional
        self.start_window = QtWidgets.QMainWindow()
        self.start_window_functional = StartWindowFunctional(self.start_window)
        self.start_window.show()
        self.main_window.close()

    def save_graph(self):
        """Сохранение графа."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Сохранить граф", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        data = {
            "vertices": [
                {
                    "id": vertex_id,
                    "params": vertex.default_params,
                    "position": {
                        "x": vertex.x,
                        "y": vertex.y
                    }
                }
                for vertex_id, vertex in self.canvas.graph.vertices.items()
            ],
            "edges": [
                {
                    "start": edge.start_vertex.id,
                    "end": edge.end_vertex.id,
                    "weight": edge.weight,
                    "params": edge.default_params
                }
                for edge in self.canvas.graph.edges
            ]
        }

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print("Граф успешно сохранён в файл:", file_path)
        except Exception as e:
            print("Ошибка при сохранении графа:", e)

    def load_graph(self):
        """Загрузка графа."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Загрузить граф", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.clear_graph()  # Очищаем текущий граф перед загрузкой нового

            # Загружаем вершины
            for vertex_data in data.get("vertices", []):
                vertex_id = vertex_data["id"]
                position = vertex_data["position"]
                params = vertex_data["params"]

                # Создаём объект вершины
                vertex = Vertex(vertex_id, x=position["x"], y=position["y"])
                vertex.default_params.update(params)
                self.canvas.graph.add_vertex(vertex)

                # Создаём визуализацию вершины вручную
                color = QColor(vertex.default_params["color"])
                radius = vertex.default_params["size"]
                x, y = position["x"], position["y"]

                ellipse = CustomEllipse(vertex_id, self.canvas, x - radius, y - radius, radius * 2, radius * 2)
                ellipse.setBrush(QBrush(color))
                ellipse.setData(0, vertex_id)

                text = QGraphicsTextItem(str(vertex_id))
                text.setParentItem(ellipse)
                text.setDefaultTextColor(QColor(vertex.default_params["text_color"]))
                text.setPos(
                    ellipse.rect().center().x() - text.boundingRect().width() / 2,
                    ellipse.rect().center().y() - text.boundingRect().height() / 2,
                )

                self.canvas.scene.addItem(ellipse)
                self.canvas.graph.vertices[vertex_id].item = ellipse

            # Загружаем рёбра
            for edge_data in data.get("edges", []):
                start_id = edge_data["start"]
                end_id = edge_data["end"]
                weight = edge_data["weight"]
                params = edge_data["params"]

                # Создаём объект ребра
                start_vertex = self.canvas.graph.vertices[start_id]
                end_vertex = self.canvas.graph.vertices[end_id]
                edge = Edge(start_vertex, end_vertex, weight=weight)
                edge.default_params.update(params)
                self.canvas.graph.edges.append(edge)

                # Создаём визуализацию ребра
                self.canvas.create_edge_visual(edge)

            self.canvas.update()  # Перерисовываем холст
            print("Граф успешно загружен из файла:", file_path)
        except Exception as e:
            print("Ошибка при загрузке графа:", e)

    def clear_graph(self):
        """Очистка графа."""
        self.canvas.graph.vertices.clear()  # Очищаем вершины в графе
        self.canvas.graph.edges.clear()  # Очищаем рёбра в графе
        self.canvas.scene.clear()  # Очищаем холст
        self.canvas.update()  # Перерисовываем холст
        print("Граф очищен")

    def toggle_graph_changing_mode(self, active):
        """Переключает режим редактирования графа с обновлением текста кнопки."""
        if active:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ✅")
            self.canvas.enable_graph_changing_mode(True)  # Включаем редактирование графа
        else:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ❌")
            self.canvas.enable_graph_changing_mode(False)  # Выключаем редактирование графа
        print(f"Режим редактирования графа: {'включен' if active else 'выключен'}")

    def run_bfs(self):
        """Выполнение алгоритма поиска в ширину."""
        print("Запущен алгоритм поиска в ширину (BFS)")

    def run_dfs(self):
        """Выполнение алгоритма поиска в глубину."""
        print("Запущен алгоритм поиска в глубину (DFS)")

    def run_dijkstra(self):
        """Выполнение алгоритма Дейкстры."""
        print("Запущен алгоритм Дейкстры")

    def run_prim(self):
        """Выполнение алгоритма Прима."""
        print("Запущен алгоритм Прима")

    def create_from_adjacency_matrix(self):
        """Создание графа по матрице смежности."""
        print("Создание графа по матрице смежности")

    def create_from_incidence_matrix(self):
        """Создание графа по матрице инцидентности."""
        print("Создание графа по матрице инцидентности")

    def create_from_edge_list(self):
        """Создание графа по списку рёбер."""
        print("Создание графа по списку рёбер")

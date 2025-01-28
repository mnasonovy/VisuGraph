from PyQt5 import QtWidgets
import json
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QGraphicsLineItem, QMessageBox, QLabel, QDockWidget
from PyQt5.QtCore import QPointF, Qt
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas  

class WorkWindowFunctional:
    def __init__(self, main_window, ui, canvas):
        self.main_window = main_window
        self.ui = ui
        self.canvas = canvas  
        self.instruction_panel = QLabel(self.main_window)
        self.instruction_panel.setStyleSheet("background-color: qlineargradient(spread:repeat, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(237, 199, 183, 255), stop:1 rgba(186, 178, 181, 255));  solid #7FFFD4; padding: 5px;")
        self.instruction_panel.setWordWrap(True)  
        self.instruction_panel.setText(self.get_editing_instructions())
        
        self.dock_widget = QDockWidget(self.main_window)
        self.dock_widget.setWidget(self.instruction_panel)
        self.dock_widget.setFloating(False)  
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)  
        self.dock_widget.setTitleBarWidget(QtWidgets.QWidget())  
        self.dock_widget.setGeometry(0, 0, 150, 50)  
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.setVisible(False) 

        self.ui.return_to_menu_action.triggered.connect(self.return_to_start_window)
        self.ui.save_graph_action.triggered.connect(self.save_graph)
        self.ui.save_weight_matrix_action.triggered.connect(self.save_weight_matrix)
        self.ui.load_graph_action.triggered.connect(self.load_graph)
        self.ui.clear_graph_action.triggered.connect(self.clear_graph)
        self.ui.graph_changing_mode_action.toggled.connect(self.toggle_graph_changing_mode)

        self.ui.bfs_action.triggered.connect(self.run_bfs)
        self.ui.dfs_action.triggered.connect(self.run_dfs)
        self.ui.dijkstra_action.triggered.connect(self.run_dijkstra)
        self.ui.prim_action.triggered.connect(self.run_prim)

    def return_to_start_window(self):
        """Возвращает пользователя в стартовое окно."""
        from GUI.functionals.start_window_functional import StartWindowFunctional
        self.start_window = QtWidgets.QMainWindow()
        self.start_window_functional = StartWindowFunctional(self.start_window)
        self.start_window.show()
        self.main_window.close()

    def save_weight_matrix(self):
        """Сохранение графа как матрицы весов с нулями на главной диагонали и None для отсутствующих рёбер."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Сохранить матрицу весов", "", "JSON Files (*.json)"
        )
        if not file_path:
            return
        size = len(self.canvas.graph.vertices)
        weight_matrix = [[0 if i == j else None for j in range(size)] for i in range(size)]

        for edge in self.canvas.graph.edges:
            start_idx = edge.start_vertex.id - 1
            end_idx = edge.end_vertex.id - 1
            weight_matrix[start_idx][end_idx] = edge.weight
            weight_matrix[end_idx][start_idx] = edge.weight  

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump({"adjacency_matrix": weight_matrix}, file, ensure_ascii=False, indent=4)
            print(f"Матрица весов сохранена в файл: {file_path}")
        except Exception as e:
            print("Ошибка при сохранении матрицы весов:", e)

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

            self.clear_graph() 

            for vertex_data in data.get("vertices", []):
                vertex_id = vertex_data["id"]
                position = vertex_data["position"]
                params = vertex_data["params"]

                vertex = Vertex(vertex_id, x=position["x"], y=position["y"])
                vertex.default_params.update(params)
                self.canvas.graph.add_vertex(vertex)

                self.canvas.create_vertex_visual(vertex)

            for edge_data in data.get("edges", []):
                start_id = edge_data["start"]
                end_id = edge_data["end"]
                weight = edge_data["weight"]
                params = edge_data["params"]

                start_vertex = self.canvas.graph.vertices[start_id]
                end_vertex = self.canvas.graph.vertices[end_id]
                edge = Edge(start_vertex, end_vertex, weight=weight)
                edge.default_params.update(params)
                self.canvas.graph.edges.append(edge)

                self.canvas.create_edge_visual(edge)
            self.canvas.update()  
            print("Граф успешно загружен из файла:", file_path)
        except Exception as e:
            print("Ошибка при загрузке графа:", e)

    def clear_graph(self):
        """Очистка графа."""
        self.canvas.graph.vertices.clear() 
        self.canvas.graph.edges.clear()  
        self.canvas.scene.clear()  
        self.canvas.update()  

    def toggle_graph_changing_mode(self, active):
        """Переключает режим редактирования графа с обновлением текста кнопки и подсказки."""
        if active:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ✅")
            self.canvas.enable_graph_changing_mode(True)  
            self.show_editing_instructions()  
        else:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ❌")
            self.canvas.enable_graph_changing_mode(False)  
            self.hide_editing_instructions()  

        print(f"Режим редактирования графа: {'включен' if active else 'выключен'}")

    def show_editing_instructions(self):
        """Показывает подсказку для пользователя о том, как редактировать граф."""
        self.dock_widget.setVisible(True)  

    def hide_editing_instructions(self):
        """Скрывает подсказку, когда режим редактирования выключен."""
        self.dock_widget.setVisible(False)  

    def get_editing_instructions(self):
        """Возвращает текст подсказки."""
        return (
            "Как редактировать граф:\n"
            "- Shift + ПКМ по вершинам - создание ребра\n"
            "- Alt + ПКМ - удаление ребра/вершины\n"
            "- Ctrl + ПКМ - создание вершины\n"
            "- Зажатая ЛКМ - перемещение вершины\n"
        )

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

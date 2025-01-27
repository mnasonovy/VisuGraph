from PyQt5 import QtWidgets
import json
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QGraphicsLineItem, QMessageBox, QLabel, QDockWidget
from PyQt5.QtCore import QPointF, Qt
from Core.graph import Vertex, Edge
from Core.vizualization import CustomEllipse, Canvas  # Убедитесь, что Canvas импортируется

class WorkWindowFunctional:
    def __init__(self, main_window, ui, canvas):
        self.main_window = main_window
        self.ui = ui
        self.canvas = canvas  # Передаем ссылку на Canvas

        # Создаем панель для подсказки, которая будет отображаться справа
        self.instruction_panel = QLabel(self.main_window)
        self.instruction_panel.setStyleSheet("background-color: qlineargradient(spread:repeat, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(237, 199, 183, 255), stop:1 rgba(186, 178, 181, 255));  solid #7FFFD4; padding: 5px;")
        self.instruction_panel.setWordWrap(True)  # Переносим текст на новую строку
        self.instruction_panel.setText(self.get_editing_instructions())
        
        # Создаем QDockWidget и прикрепляем подсказку к нему
        self.dock_widget = QDockWidget(self.main_window)
        self.dock_widget.setWidget(self.instruction_panel)
        self.dock_widget.setFloating(False)  # Не плавающая панель
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Отключаем возможность "открепления"

        # Убираем заголовок панели (черную полосу)
        self.dock_widget.setTitleBarWidget(QtWidgets.QWidget())  # Убираем заголовок

        # Устанавливаем размер панели
        self.dock_widget.setGeometry(0, 0, 150, 50)  # Устанавливаем размеры (ширина 250px, высота 100px)

        # Прикрепляем панель с подсказкой справа
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.dock_widget.setVisible(False)  # Скрываем панель по умолчанию

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

                # Используем функцию create_vertex_visual для создания визуализации вершины
                self.canvas.create_vertex_visual(vertex)

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

    def toggle_graph_changing_mode(self, active):
        """Переключает режим редактирования графа с обновлением текста кнопки и подсказки."""
        if active:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ✅")
            self.canvas.enable_graph_changing_mode(True)  # Включаем редактирование графа
            self.show_editing_instructions()  # Показываем подсказку
        else:
            self.ui.graph_changing_mode_action.setText("Режим редактирования графа ❌")
            self.canvas.enable_graph_changing_mode(False)  # Выключаем редактирование графа
            self.hide_editing_instructions()  # Скрываем подсказку

        print(f"Режим редактирования графа: {'включен' if active else 'выключен'}")

    def show_editing_instructions(self):
        """Показывает подсказку для пользователя о том, как редактировать граф."""
        self.dock_widget.setVisible(True)  # Показываем панель с подсказкой

    def hide_editing_instructions(self):
        """Скрывает подсказку, когда режим редактирования выключен."""
        self.dock_widget.setVisible(False)  # Скрываем панель с подсказкой

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

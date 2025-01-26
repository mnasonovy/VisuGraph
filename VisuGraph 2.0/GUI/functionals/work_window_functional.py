from PyQt5 import QtWidgets

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
        self.ui.graph_creation_mode_action.toggled.connect(self.toggle_graph_creation_mode)

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
        print("Граф сохранен")

    def load_graph(self):
        """Загрузка графа."""
        print("Граф загружен")

    def clear_graph(self):
        """Очистка графа."""
        print("Граф очищен")

    def toggle_graph_creation_mode(self, active):
        """Переключает режим создания графа с обновлением текста кнопки."""
        if active:
            self.ui.graph_creation_mode_action.setText("Режим создания графа ✅")
            self.canvas.enable_node_creation_mode(True)  # Включаем создание вершины
        else:
            self.ui.graph_creation_mode_action.setText("Режим создания графа ❌")
            self.canvas.enable_node_creation_mode(False)  # Выключаем создание вершины
        print(f"Режим создания графа: {'включен' if active else 'выключен'}")

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


from PyQt5 import QtCore, QtGui, QtWidgets
from Core.vizualization import Canvas  # Импортируем Canvas для визуализации графа
from Core.graph import Graph  # Импортируем Graph, чтобы передавать его в Canvas
from GUI.functionals.work_window_functional import WorkWindowFunctional
from Algorithms.sacred_algorihm import SacredAlgorithm  # Импортируем SacredAlgorithm
from GUI.creating.creating_graph import (
    create_graph_from_edge_list,
    create_graph_from_adjacency_matrix,
    create_graph_from_incidence_matrix,
)

class Ui_WorkWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2000, 900)
        MainWindow.setStyleSheet(
            "background-color: qlineargradient(spread:repeat, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(237, 199, 183, 255), stop:1 rgba(186, 178, 181, 255));"
        )

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Создаём объект Graph
        self.graph = Graph()

        # Статически задаем размеры холста
        self.canvas_width = 1600  # Статическое значение ширины холста
        self.canvas_height = 800  # Статическое значение высоты холста
        
        # Создаём объект Canvas, передаем graph и self (UI)
        self.canvas = Canvas(self.graph, self.centralwidget)
        self.canvas.setObjectName("canvas")
        
        # Используем QVBoxLayout для адаптивного размещения
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.addWidget(self.canvas)
        
        # Устанавливаем пропорцию для холста (85% от высоты и ширины)
        self.layout.setStretchFactor(self.canvas, 85)
        
        MainWindow.setCentralWidget(self.centralwidget)

        # Создаем объект SacredAlgorithm
        self.sacred_algorithm = SacredAlgorithm(self.canvas)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1500, 21))
        self.menubar.setObjectName("menubar")
        
        # Меню действий
        self.action_menu = QtWidgets.QMenu(self.menubar)
        self.action_menu.setTitle("Меню действий")
        self.action_menu.setObjectName("action_menu")

        self.save_graph_action = QtWidgets.QAction("Сохранить граф", MainWindow)
        self.load_graph_action = QtWidgets.QAction("Загрузить граф", MainWindow)
        self.clear_graph_action = QtWidgets.QAction("Очистить", MainWindow)
        self.return_to_menu_action = QtWidgets.QAction("В главное меню", MainWindow)

        self.action_menu.addAction(self.save_graph_action)
        self.action_menu.addAction(self.load_graph_action)
        self.action_menu.addAction(self.clear_graph_action)
        self.action_menu.addAction(self.return_to_menu_action)

        # Режим создания графа
        self.graph_changing_mode_action = QtWidgets.QAction("Режим редактирования графа ❌", MainWindow)
        self.graph_changing_mode_action.setCheckable(True)
        self.graph_changing_mode_action.setObjectName("graph_changing_mode_action")

        # Меню алгоритмов
        self.algorithms_menu = QtWidgets.QMenu(self.menubar)
        self.algorithms_menu.setTitle("Алгоритмы")
        self.algorithms_menu.setObjectName("algorithms_menu")

        self.bfs_action = QtWidgets.QAction("Поиск в ширину (BFS)", MainWindow)
        self.dfs_action = QtWidgets.QAction("Поиск в глубину (DFS)", MainWindow)
        self.dijkstra_action = QtWidgets.QAction("Алгоритм Дейкстры", MainWindow)
        self.prim_action = QtWidgets.QAction("Алгоритм Прима", MainWindow)
        self.sacred_algorithm_action = QtWidgets.QAction("Sacred Algorithm", MainWindow)  # Измененная кнопка

        self.algorithms_menu.addAction(self.bfs_action)
        self.algorithms_menu.addAction(self.dfs_action)
        self.algorithms_menu.addAction(self.dijkstra_action)
        self.algorithms_menu.addAction(self.prim_action)
        self.algorithms_menu.addAction(self.sacred_algorithm_action)

        # Связь кнопки Sacred Algorithm с методом sacred_algorithm_calling
        self.sacred_algorithm_action.triggered.connect(self.sacred_algorithm.sacred_algorithm_calling)

        # Меню создания графа
        self.create_graph_menu = QtWidgets.QMenu(self.menubar)
        self.create_graph_menu.setTitle("Создать граф")
        self.create_graph_menu.setObjectName("create_graph_menu")

        self.adjacency_matrix_action = QtWidgets.QAction("По матрице смежности", MainWindow)
        self.adjacency_matrix_action.triggered.connect(
            lambda: create_graph_from_adjacency_matrix(self.canvas, self.functional)  # Вызываем clear_graph через functional
        )

        self.incidence_matrix_action = QtWidgets.QAction("По матрице инцидентности", MainWindow)
        self.incidence_matrix_action.triggered.connect(
            lambda: create_graph_from_incidence_matrix(self.canvas, self.functional)  # Вызываем clear_graph через functional
        )

        self.edge_list_action = QtWidgets.QAction("По списку рёбер", MainWindow)
        self.edge_list_action.triggered.connect(
            lambda: create_graph_from_edge_list(self.canvas, self.functional)  # Вызываем clear_graph через functional
        )

        self.create_graph_menu.addAction(self.adjacency_matrix_action)
        self.create_graph_menu.addAction(self.incidence_matrix_action)
        self.create_graph_menu.addAction(self.edge_list_action)

        # Добавление меню в меню bar
        self.menubar.addMenu(self.action_menu)
        self.menubar.addAction(self.graph_changing_mode_action)
        self.menubar.addMenu(self.algorithms_menu)
        self.menubar.addMenu(self.create_graph_menu)

        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Подключение функционала
        self.functional = WorkWindowFunctional(MainWindow, self, self.canvas)  # Передаем canvas

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VisuGraph"))

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(600, 400)

        SettingsWindow.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, "
            "stop:0 rgba(0, 128, 255, 255), stop:1 rgba(255, 255, 255, 255));"
            "border: 2px solid rgb(0, 100, 0);"
        )

        self.centralwidget = QtWidgets.QWidget(SettingsWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.main_node_button = QtWidgets.QPushButton(self.centralwidget)
        self.main_node_button.setGeometry(QtCore.QRect(200, 50, 200, 40))
        self.main_node_button.setStyleSheet(
            "background-color: rgb(0, 255, 0);"
            "color: rgb(0, 0, 0);"
            "border-radius: 10px;"
        )
        self.main_node_button.setObjectName("main_node_button")

        self.selected_node_button = QtWidgets.QPushButton(self.centralwidget)
        self.selected_node_button.setGeometry(QtCore.QRect(200, 100, 200, 40))
        self.selected_node_button.setStyleSheet(
            "background-color: rgb(255, 165, 0);"
            "color: rgb(0, 0, 0);"
            "border-radius: 10px;"
        )
        self.selected_node_button.setObjectName("selected_node_button")

        self.main_edge_button = QtWidgets.QPushButton(self.centralwidget)
        self.main_edge_button.setGeometry(QtCore.QRect(200, 150, 200, 40))
        self.main_edge_button.setStyleSheet(
            "background-color: rgb(255, 0, 0);"
            "color: rgb(255, 255, 255);"
            "border-radius: 10px;"
        )
        self.main_edge_button.setObjectName("main_edge_button")

        self.selected_edge_button = QtWidgets.QPushButton(self.centralwidget)
        self.selected_edge_button.setGeometry(QtCore.QRect(200, 200, 200, 40))
        self.selected_edge_button.setStyleSheet(
            "background-color: rgb(0, 0, 255);"
            "color: rgb(255, 255, 255);"
            "border-radius: 10px;"
        )
        self.selected_edge_button.setObjectName("selected_edge_button")

        self.background_button = QtWidgets.QPushButton(self.centralwidget)
        self.background_button.setGeometry(QtCore.QRect(200, 250, 200, 40))
        self.background_button.setStyleSheet(
            "background-color: rgb(255, 255, 0);"
            "color: rgb(0, 0, 0);"
            "border-radius: 10px;"
        )
        self.background_button.setObjectName("background_button")

        self.return_to_menu_button = QtWidgets.QPushButton(self.centralwidget)
        self.return_to_menu_button.setGeometry(QtCore.QRect(200, 300, 200, 40))
        self.return_to_menu_button.setStyleSheet(
            "background-color: rgb(128, 0, 128);"
            "color: rgb(255, 255, 255);"
            "border-radius: 10px;"
        )
        self.return_to_menu_button.setObjectName("return_to_menu_button")

        SettingsWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SettingsWindow)
        QtCore.QMetaObject.connectSlotsByName(SettingsWindow)

    def retranslateUi(self, SettingsWindow):
        _translate = QtCore.QCoreApplication.translate
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "Настройки графа"))
        self.main_node_button.setText(_translate("SettingsWindow", "Настройка основной вершины"))
        self.selected_node_button.setText(_translate("SettingsWindow", "Настройка выделенной вершины"))
        self.main_edge_button.setText(_translate("SettingsWindow", "Настройка основного ребра"))
        self.selected_edge_button.setText(_translate("SettingsWindow", "Настройка выделенного ребра"))
        self.background_button.setText(_translate("SettingsWindow", "Настройка заднего фона"))
        self.return_to_menu_button.setText(_translate("SettingsWindow", "В главное меню"))

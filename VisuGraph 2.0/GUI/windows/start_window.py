from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_start_window(object):
    def setupUi(self, start_window):
        self.start_window = start_window  
        start_window.setObjectName("start_window")
        start_window.resize(400, 500)
        start_window.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        start_window.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(24, 40, 51, 255), stop:1 rgba(11, 12, 16, 255));"
        )

        self.centralwidget = QtWidgets.QWidget(start_window)
        self.centralwidget.setObjectName("centralwidget")

        self.create_graph_button = QtWidgets.QPushButton(self.centralwidget)
        self.create_graph_button.setGeometry(QtCore.QRect(100, 100, 200, 50))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.create_graph_button.setFont(font)
        self.create_graph_button.setStyleSheet("background-color: rgb(53, 0, 211);\ncolor: rgb(102, 252, 241);")
        self.create_graph_button.setObjectName("create_graph_button")

        self.settings_button = QtWidgets.QPushButton(self.centralwidget)
        self.settings_button.setGeometry(QtCore.QRect(100, 170, 200, 50))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.settings_button.setFont(font)
        self.settings_button.setStyleSheet("background-color: rgb(25, 0, 97);\ncolor: rgb(102, 252, 241);")
        self.settings_button.setObjectName("settings_button")

        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(100, 240, 200, 50))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.exit_button.setFont(font)
        self.exit_button.setStyleSheet("background-color: rgb(12, 0, 50);\ncolor: rgb(102, 252, 241);")
        self.exit_button.setObjectName("exit_button")

        start_window.setCentralWidget(self.centralwidget)

        self.retranslateUi(start_window)
        QtCore.QMetaObject.connectSlotsByName(start_window)

    def retranslateUi(self, start_window):
        _translate = QtCore.QCoreApplication.translate
        start_window.setWindowTitle(_translate("start_window", "VisuGraph"))
        self.create_graph_button.setText(_translate("start_window", "Создать новый граф"))
        self.settings_button.setText(_translate("start_window", "Настройки графа"))
        self.exit_button.setText(_translate("start_window", "Выйти"))

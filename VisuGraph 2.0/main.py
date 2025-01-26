import sys
from PyQt5 import QtWidgets
from GUI.functionals.start_window_functional import StartWindowFunctional

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    start_window = StartWindowFunctional(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

from PyQt5 import QtWidgets
from GUI.windows.start_window import Ui_start_window
from GUI.windows.work_window import Ui_WorkWindow
from GUI.windows.settings_window import Ui_SettingsWindow

class StartWindowFunctional:
    def __init__(self, start_window):
        self.start_window = start_window
        self.ui = Ui_start_window()
        self.ui.setupUi(self.start_window)
        
        # Подключаем кнопки к методам
        self.ui.create_graph_button.clicked.connect(self.open_work_window)
        self.ui.settings_button.clicked.connect(self.open_settings_window)
        self.ui.exit_button.clicked.connect(self.exit_application)

    def open_work_window(self):
        """Открывает окно для работы с графом."""
        self.work_window = QtWidgets.QMainWindow()
        self.ui_work = Ui_WorkWindow()
        self.ui_work.setupUi(self.work_window)
        self.work_window.show()
        self.start_window.hide()

    def open_settings_window(self):
        """Открывает окно настроек."""
        self.settings_window = QtWidgets.QMainWindow()
        self.ui_settings = Ui_SettingsWindow()
        self.ui_settings.setupUi(self.settings_window)
        self.settings_window.show()
        self.start_window.hide()

    def exit_application(self):
        """Закрывает приложение."""
        QtWidgets.QApplication.instance().quit()

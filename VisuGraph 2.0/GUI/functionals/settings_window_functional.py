from PyQt5 import QtWidgets
from GUI.windows.settings_window import Ui_SettingsWindow
from GUI.functionals.start_window_functional import StartWindowFunctional

class SettingsWindowFunctional:
    def __init__(self, settings_window):
        self.settings_window = settings_window
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self.settings_window)

        # Подключение кнопок к методам
        self.ui.return_to_menu_button.clicked.connect(self.return_to_main_menu)

    def return_to_main_menu(self):
        """Возвращает пользователя в главное меню."""
        self.main_menu = QtWidgets.QMainWindow()
        self.start_window_functional = StartWindowFunctional(self.main_menu)
        self.main_menu.show()
        self.settings_window.close()

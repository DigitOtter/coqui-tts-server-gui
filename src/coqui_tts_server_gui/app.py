from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

import sys
import os

from matplotlib.pyplot import show

from coqui_tts_server_gui.gui.main_window import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName('coqui_ai_tts_server_gui')
    app.setOrganizationName('digitotter')

    cwd = os.path.dirname(os.path.abspath(__file__))
    icon_file = os.path.join(cwd, 'icon.ico')
    icon = QIcon(icon_file)

    # Setup Main Window
    window = MainWindow()
    window.setWindowIcon(icon)

    # Setup tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.activated.connect(window.show)

    # Create tray options
    menu = QMenu()

    show_window = QAction("Show Window")
    show_window.triggered.connect(window.show_window)
    menu.addAction(show_window)

    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    
    # Add options to system tray
    tray.setContextMenu(menu)

    # Start server
    window.start_server()

    # Show window, start Qt event loop
    window.show()
    app.exec()

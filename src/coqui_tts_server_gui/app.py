from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QSystemSemaphore, QSharedMemory

import sys
import os

from coqui_tts_server_gui.gui.main_window import MainWindow


def check_if_running(app_name: str, shared_memory: QSharedMemory) -> bool:
    """
    Ensures that only one instance of app is started.
    Code taken from https://stackoverflow.com/questions/65717815/how-can-i-make-my-pyqt5-app-oney-one-instance
    """
    semaphore = QSystemSemaphore(app_name, 1)
    semaphore.acquire()  # Raise the semaphore, barring other instances to work with shared memory

    if sys.platform != 'win32':
        # in linux / unix shared memory is not freed when the application terminates abnormally,
        # so you need to get rid of the garbage
        nix_fix_shared_mem = QSharedMemory(shared_memory.key())
        if nix_fix_shared_mem.attach():
            nix_fix_shared_mem.detach()

    if shared_memory.attach(QSharedMemory.AccessMode.ReadWrite):  # attach a copy of the shared memory, if successful, the application is already running
        is_running = True
    else:
        shared_memory.create(1, QSharedMemory.AccessMode.ReadWrite)  # allocate a shared memory block of 1 byte
        is_running = False

    semaphore.release()

    return is_running


if __name__ == '__main__':
    app_name: str = 'coqui_ai_tts_server_gui'

    app = QtWidgets.QApplication(sys.argv)

    shared_memory = QSharedMemory("coqui_ai_tts_server_gui_shmem")
    if check_if_running(app_name, shared_memory):
        print("CoquiAI TTS GUI already running")
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(app_name)
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

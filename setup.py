from setuptools import setup, find_packages
import setuptools
from setuptools.command.build_py import build_py
import os
import subprocess

pkg_name = 'coqui_tts_server_gui'

cwd = os.path.dirname(os.path.abspath(__file__))

# Read requirements
requirements = open(os.path.join(cwd, "requirements.txt"), "r").readlines()

# Create pyqt files
class PyQtBuildPy(build_py):
    def run(self):
        main_window_ui    = os.path.join(cwd, 'forms/main_window.ui')
        main_window_ui_py = os.path.join(self.build_lib, pkg_name, 'uic/main_window_ui.py')

        os.makedirs(os.path.dirname(main_window_ui_py), exist_ok=True)
        subprocess.call([os.sys.executable, '-m', 'PyQt6.uic.pyuic', '-o', main_window_ui_py, '-x', main_window_ui])

        build_py.run(self)


setup(
    install_requires=requirements,
    # entry_points={
    #     'console_scripts': ['coqui-tts-server-gui=exampleproject.example:main']
    # },
    cmdclass={'build_py': PyQtBuildPy}
)

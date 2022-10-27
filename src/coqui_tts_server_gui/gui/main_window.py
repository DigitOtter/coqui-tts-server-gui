from PyQt6 import QtWidgets, uic
from TTS.utils.manage import ModelManager

from coqui_tts_server_gui.gui.main_window_ui import Ui_MainWindow
from coqui_tts_server_gui.tts_server_ctrl import TtsServerCtrl
from coqui_tts_server_gui.tts_server_settings import TtsServerSettings


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        #super().__init__(*args, **kwargs)
        #uic.loadUi("forms/main_window.ui", self)

        self.settings = TtsServerSettings()
        
        self.tts_model_manager = ModelManager()

        # Get TTS Models, set default model to top of list
        tts_models = self.tts_model_manager.list_tts_models()
        if self.settings.default_tts_model in tts_models:
            tts_models.remove(self.settings.default_tts_model)
            tts_models.insert(0, self.settings.default_tts_model)

        self.model_name_box.addItems(tts_models)
        self.settings.add_handler('model_name', self.model_name_box)

        vocoder_models = self.tts_model_manager.list_vocoder_models()
        vocoder_models.insert(0, 'None')
        self.vocoder_name_box.addItems(vocoder_models)
        self.settings.add_handler('vocoder_name', self.vocoder_name_box)

        self.address_text.setDisabled(True)
        self.settings.add_handler('address_text', self.address_text)
        self.settings.add_handler('port_text', self.port_text)

        self.tts_server_ctrl = TtsServerCtrl()

        self.connect_button.clicked.connect(self._connect_clicked)

    def _connect_clicked(self):
        model_name = 'tts_models/' + self.model_name_box.currentText()
        
        vocoder_name = self.vocoder_name_box.currentText()
        if not vocoder_name or vocoder_name == 'None':
            vocoder_name = None
        else:
            vocoder_name = 'vocoder_models/' + vocoder_name

        port = int(self.port_text.text()) if self.port_text.text() else 5002
        self.tts_server_ctrl._start_server( tts_server_executable=self.settings.tts_server_executable, 
                                            model_name=model_name,
                                            port=port)

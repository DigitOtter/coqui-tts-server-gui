from PyQt6 import QtWidgets, QtGui, uic
from TTS.utils.manage import ModelManager

from coqui_tts_server_gui.gui.main_window_ui import Ui_MainWindow
from coqui_tts_server_gui.tts_server_ctrl import TtsServerCtrl
from coqui_tts_server_gui.tts_server_settings import TtsServerSettings
from coqui_tts_server_gui.tts_server_audio import TtsServerAudio


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs) -> None:
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

        # List available TTS models
        self.model_name_box.addItems(tts_models)

        # List available vocoder models
        vocoder_models = self.tts_model_manager.list_vocoder_models()
        vocoder_models.insert(0, 'None')
        self.vocoder_name_box.addItems(vocoder_models)

        # For now, only allow localhost as server address
        self.address_text.setDisabled(True)

        # Save selected options
        self.settings.add_handler('address_text', self.address_text)
        self.settings.add_handler('port_text', self.port_text)
        self.settings.add_handler('speaker_id', self.speaker_id_box)
        self.settings.add_handler('model_name', self.model_name_box)
        self.settings.add_handler('vocoder_name', self.vocoder_name_box)

        # Setup TTS server proc interface
        self.tts_server_ctrl  = TtsServerCtrl(self)
        self.tts_server_ctrl.connect_proc_with_status_bar(self.statusbar)
        self.statusbar.showMessage("FDSAFDASFD")
        
        self.tts_server_audio = TtsServerAudio()

        self.tts_server_addr = self.tts_address()

        # Connect buttons
        self.connect_button.clicked.connect(self._connect_clicked)
        self.tts_convert_button.clicked.connect(self._tts_clicked)

    def show_window(self) -> None:
        """Show window and bring to focus"""
        self.activateWindow()
        self.raise_()
        self.show()

    def start_server(self):
        """Start server"""
        return self._connect_clicked()

    def tts_port(self) -> int:
        return int(self.port_text.text() if self.port_text.text() else self.port_text.placeholderText())

    def tts_address(self) -> str:
        address: str = self.address_text.text() if self.address_text.text() else self.address_text.placeholderText()
        return f"{address}:{self.tts_port()}"

    def update_tts_speaker_ids(self) -> None:
        """Request available speaker_ids from server"""
        self.speaker_id_box.clear()
        self.speaker_id_box.setDisabled(True)

        if not self.tts_server_ctrl.wait_tts_server_start():
            return

        speaker_ids, _ = self.tts_server_ctrl.get_tts_speaker_ids()
        
        if speaker_ids:
            # Workaround to remove speakers containing newlines
            speaker_ids = [ speaker_id for speaker_id in speaker_ids if not "\n" in speaker_id ]
            self.speaker_id_box.setDisabled(False)
            self.speaker_id_box.addItems(speaker_ids)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """Close server process before closing"""
        self.tts_server_ctrl.close_proc()
        return super().closeEvent(a0)

    def _connect_clicked(self) -> None:
        """Restart server with selected TTS models on selected port. Also updates speaker_ids"""
        self.speaker_id_box.setDisabled(True)

        model_name = f"tts_models/{self.model_name_box.currentText()}"
        
        vocoder_name = self.vocoder_name_box.currentText()
        if not vocoder_name or vocoder_name == 'None':
            vocoder_name = None
        else:
            vocoder_name = f"vocoder_models/{vocoder_name}"

        self.tts_server_addr = self.tts_address()

        self.tts_server_ctrl._start_server( 
            tts_server_executable=self.settings.tts_server_executable, 
            model_name=model_name,
            port=self.tts_port(),
            vocoder_name=vocoder_name)
        
        self.update_tts_speaker_ids()
    
    def _tts_clicked(self) -> None:
        """Send text to TTS server and play audio"""
        # Don't try to play audio if server is restarting
        if self.tts_server_ctrl.restarting:
            return

        speaker_id = self.speaker_id_box.currentText() if self.speaker_id_box.count() else None
        wav_bytes, response = self.tts_server_ctrl.get_tts_audio(
            tts_text=self.tts_text_box.toPlainText(),
            speaker_id=speaker_id)
        
        if wav_bytes:
            self.tts_server_audio.async_play(wav_bytes=wav_bytes)

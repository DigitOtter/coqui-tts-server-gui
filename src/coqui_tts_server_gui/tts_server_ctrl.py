from functools import partial
import json
import math
from PyQt6.QtCore import pyqtSignal, QObject, QProcess, QCoreApplication
from PyQt6.QtWidgets import QStatusBar
import requests
import threading
import time


class TtsServerCtrl(QObject):
    tts_proc_status_message = pyqtSignal([str])

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.port: int = 5002
        self.mutex: threading.Lock = threading.Lock()
        self.serv_proc: QProcess = QProcess()
        self.serv_proc.started.connect(self.__proc_started)
        self.serv_proc.errorOccurred.connect(self.__proc_error)
        self.serv_proc.finished.connect(self.__proc_finished)
        self.restarting = False
        self.__server_status_thread = threading.Thread(target=self.__update_status_bar)

    def _start_server(self, tts_server_executable, model_name, port=None, vocoder_name=None) -> None:
        """Stops currently running server and respawns a new one with the given arguments"""
        self.restarting = True
        if self.__server_status_thread.is_alive():
            self.__server_status_thread.join()

        with self.mutex:
            self.port: int = port if port is not None else self.port

            # Emit signal before killing server
            self.tts_proc_status_message.emit("Starting TTS Server process...")
            QCoreApplication.processEvents()

            if self.serv_proc.state() != QProcess.ProcessState.NotRunning:
                self.__close_proc_nonblocking()
                self.serv_proc.waitForFinished()
                time.sleep(2)

            srv_args = [
                '--model_name', model_name,
                '--port', str(port),
                '--subproc', "True"
            ]
            if vocoder_name:
                srv_args.extend(['--vocoder_name', vocoder_name])

            if not tts_server_executable:
                print("Failed to find TTS server executable")

            # Emit signal before restarting server
            self.tts_proc_status_message.emit("Starting TTS Server...")
            QCoreApplication.processEvents()

            # Start server
            self.serv_proc.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
            self.serv_proc.start(tts_server_executable, arguments=srv_args)
            self.serv_proc.waitForStarted()

            self.restarting = False

            self.__server_status_thread = threading.Thread(target=self.__update_status_bar)
            self.__server_status_thread.start()

    def __close_proc_nonblocking(self) -> None:
        self.__call_server_shutdown_nonblocking()
        self.serv_proc.terminate()
        if not self.serv_proc.waitForFinished(msecs=1000):
            self.serv_proc.kill()

    def close_proc(self) -> None:
        return self.__close_proc_nonblocking()

    def _server_url(self) -> str:
        return f'http://localhost:{self.port}'

    def is_tts_server_running(self) -> bool:
        with self.mutex:
            return self.__is_tts_server_running_nonblocking()

    def __is_tts_server_running_nonblocking(self) -> bool:
        QCoreApplication.processEvents()
        if self.serv_proc.state() == QProcess.ProcessState.NotRunning:
            return None

        try:
            response: requests.Response = requests.get(f"{self._server_url()}/api/is_running")
        except requests.ConnectionError:
            return False

        return response.ok

    def wait_tts_server_start(self, timeout: float = None) -> bool:
        stop_time: float = time.time() + timeout if timeout else math.inf
        while stop_time > time.time():
            stat = self.is_tts_server_running()
            # Return false if server not running
            if stat is None:
                return False
            
            if stat == True:
                return True
            
            time.sleep(0.01)
        
        return False

    def __call_server_shutdown_nonblocking(self) -> bool:
        QCoreApplication.processEvents()
        if self.serv_proc.state() == QProcess.ProcessState.NotRunning:
            return None
        
        try:
            response: requests.Response = requests.get(f"{self._server_url()}/api/shutdown")
        except requests.ConnectionError:
            return False
        
        return response.ok

    def call_server_shutdown(self) -> bool:
        with self.mutex:
            return self.__call_server_shutdown_nonblocking()

    def get_tts_audio(self, tts_text: str, speaker_id: int=None) -> tuple[bytearray, requests.Response]:
        with self.mutex:
            if self.serv_proc.state() != QProcess.ProcessState.Running:
                return (None, None)

            params = [("text", tts_text), ("style_wav", "")]
            if speaker_id is not None:
                params.append(("speaker_id", str(speaker_id)))
            
            try:
                response: requests.Response = requests.get(f"{self._server_url()}/api/tts", params=params)
            except requests.ConnectionError:
                return (None, None)

            return (response.content if response.ok else None, response)

    def get_tts_speaker_ids(self) -> tuple[list, requests.Response]:
        """Gets speaker id from server"""
        with self.mutex:
            if self.serv_proc.state() != QProcess.ProcessState.Running:
                return None, None
        
            response: requests.Response = requests.get(f"{self._server_url()}/speaker_ids")
            
            if not response.ok:
                return None, response

            try:
                return (list(json.loads(response.content).keys()), response)
            except ValueError:
                return (None, response)

    def connect_proc_with_status_bar(self, status_bar: QStatusBar) -> None:
        """Connect process status with status bar"""
        self.tts_proc_status_message.connect(status_bar.showMessage)

    def __proc_started(self) -> None:
        self.tts_proc_status_message.emit("TTS server process starting...")

    def __proc_finished(self) -> None:
        self.tts_proc_status_message.emit("TTS server process finished")

    def __proc_error(self, error: QProcess.ProcessError) -> None:
        self.tts_proc_status_message.emit(f"TTS server process error: {error}")

    def __update_status_bar(self) -> None:
        self.tts_proc_status_message.emit("Starting TTS Server...")
        while not self.restarting:
            if self.is_tts_server_running():
                self.tts_proc_status_message.emit("TTS server process started")
                break

            time.sleep(0.1)

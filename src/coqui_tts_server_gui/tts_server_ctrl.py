from PyQt6.QtCore import QProcess
import threading


class TtsServerCtrl:
    def __init__(self):
        self.mutex = threading.Lock()
        self.serv_proc = QProcess()
    
    def _start_server(self, tts_server_executable, model_name, port=5002, vocoder_name=None):
        """Stops currently running server and respawns a new one with the given arguments"""
        with self.mutex:
            if self.serv_proc.state() != QProcess.ProcessState.NotRunning:
                self.serv_proc.kill()
                if not self.serv_proc.waitForFinished(msecs=5*1000):
                    self.serv_proc.terminate()

            srv_args = [
                '--model_name', model_name,
                '--port', str(port)
            ]
            if vocoder_name:
                srv_args.extend(['--vocoder_name', vocoder_name])

            self.serv_proc.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedOutputChannel)
            self.serv_proc.start(tts_server_executable, arguments=srv_args)

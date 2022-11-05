from pyqtconfig import QSettingsManager
import configparser
import os
from shutil import which


CONFIG_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')


class TtsServerSettings(QSettingsManager):
    def __init__(self, *args, **kwargs) -> None:
        super(TtsServerSettings, self).__init__(*args, **kwargs)
        
        self.config = configparser.ConfigParser()
        print(CONFIG_FILE)
        self.config.read(CONFIG_FILE)

    @property
    def rel_executable_dir(self) -> str:
        exec_dir = self.config['tts-server']['RelExecDir']
        return exec_dir if exec_dir else None

    @property
    def tts_server_executable(self) -> str:
        exec_name = self.config['tts-server']['Executable']
        rel_exec_dir = self.rel_executable_dir
        rel_exec_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_exec_dir) if rel_exec_dir else None
        
        tts_server_exec = which(exec_name, path=rel_exec_dir)
        if not tts_server_exec and rel_exec_dir:
            tts_server_exec = which(exec_name, path=None)
        return tts_server_exec
    
    @property
    def default_tts_model(self) -> str:
        return self.config['tts-server']['DefaultTtsModel']

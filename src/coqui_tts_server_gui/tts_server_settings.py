from pyqtconfig import QSettingsManager
import configparser
import os


CONFIG_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
#CONFIG_FILE='config.ini'

class TtsServerSettings(QSettingsManager):
    def __init__(self, *args, **kwargs):
        super(TtsServerSettings, self).__init__(*args, **kwargs)
        
        self.config = configparser.ConfigParser()
        print(CONFIG_FILE)
        self.config.read(CONFIG_FILE)

    @property
    def tts_server_executable(self):
        return self.config['tts-server']['Executable']
    
    @property
    def default_tts_model(self):
        return self.config['tts-server']['DefaultTtsModel']

    
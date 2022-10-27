#!/bin.bash

pyinstaller --collect-all TTS --collect-data trainer --collect-data librosa --collect-binaries torchaudio --collect-data gruut --collect-data unidic_lite --collect-all pycrfsuite --collect-data jamo --noconfirm -F ../src/tts_server_wrapper/tts_server_wrapper.py

pyinstaller --collect-all TTS --collect-data trainer --add-data '../src/coqui_tts_server_gui/config.ini;coqui_tts_server_gui' --add-data '../src/coqui_tts_server_gui/icon.ico;.' --add-binary "tts-server.exe;coqui_tts_server_gui\tts-server-bin" --noconfirm -F ../src/coqui_tts_server_gui/app.py


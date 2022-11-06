# coqui-tts-server-gui

A GUI Interface for the CoquiAI TTS server. 

## Overview

This program starts a TTS server with the selected model. It provides access to a range of freely available TTS models that can be run on your local machine. The server can also be used by other apps that need TTS functionality, for example [Firebot](https://github.com/DigitOtter/firebot-script-coqui-ai-tts).

![CoquiAI TTS GUI Example](/images/coqui_ai_tts_gui_example.png "CoquiAI TTS GUI Example")

## Installation

### For Windows
- Download `coqui-tts-server-gui-win.exe` from [Releases](https://github.com/DigitOtter/firebot-script-coqui-ai-tts/releases)
- Copy `coqui-tts-server-gui.exe` to your desired location
- To start the server, launch `coqui-tts-server-gui.exe`. The included GUI automatically starts a TTS server at `http://localhost:5002`

### For Linux
- Ensure that either `espeak` or `espeak-ng` is installed (e.g. via `sudo apt install espeak`)
- Clone the local repository
- Download submodules with `git submodule update --init -recursive`
- To install, use

  ```python
  python -m venv venv
  pip install wheel
  pip install "third-party/coqui-ai-tts"
  pip install .
  ```

- The program can then be started by running `coqui-tts-server-gui` from the created `venv`

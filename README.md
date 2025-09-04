# scope_emu_demo
Oscilloscope X-Y Mode Emulator
tested on Python 3.9

## Prerequisites
* Python 3.9+
* MacOS
```shell
brew install portaudio
```
* Linux (Debian/Ubuntu)
```shell
sudo apt install libportaudio2 libportaudiocpp0
```
* Windows: additional actions are not required

## Setup
1. Download http://luis.net/projects/scope/beams_4ch.wav
2. Run
```shell
python3 -m venv venv
```
Mac/Linux:
```shell
source venv/bin/activate
```
Windows:
```shell
venv\Scripts\activate.bat
```
```shell
pip install -r requirements.txt
```

## Run demo
```shell
python3 ./scope_emu.py -i beams_4ch.wav -g False -l True
```

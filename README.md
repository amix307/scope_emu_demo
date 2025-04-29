# scope_emu_demo
Oscilloscope X-Y Mode Emulator
tested on Python 3.9

download http://luis.net/projects/scope/beams_4ch.wav

python3 -m venv venv

source venv/bin/activate

(venv) pip install -r requirements.txt

(venv) python3 ./scope_emu.py -i beams_4ch.wav -g False -l True

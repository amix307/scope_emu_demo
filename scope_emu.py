#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Oscilloscope X-Y Mode Emulator
#
# (c)2007 Felipe Sanches
# (c)2007 Leandro Lameiro
# licensed under GNU GPL v3 or later
#
# A bunch of bug fixes and enhancements
#   Michael Sparmann, 2009
#
# Additional improvements and optimizations
#   Luis Gonzalez, 2014
#
# Python 3 port and minor clean-ups
#   2025 amix307

import sys
import getopt
import struct
import wave
import subprocess as sp

import pyaudio
import pygame
import pygame.surfarray as surfarray

exportVideo  = False           # video export
showGrid     = False           # grid
listenInput  = True            # sound
musix        = "beams_4ch.wav"
app_title    = "Oscilloscope X-Y Mode Emulator"

helpText = (f"{app_title}\n\n"
            "  scope_emu.py -i <inputfile> -g <showGridBoolean> "
            "-l <listenInputBoolean> -e <exportBoolean>\n")

try:
    opts, _ = getopt.getopt(
        sys.argv[1:],
        "h:i:g:l:e:",
        ["help", "ifile", "grid", "listen", "export"]
    )
except getopt.GetoptError:
    print(helpText)
    sys.exit(2)

for opt, arg in opts:
    arg = arg.strip()
    if opt in ("-h", "--help"):
        print(helpText)
        sys.exit()
    elif opt in ("-i", "--ifile"):
        musix = arg
    elif opt in ("-g", "--grid"):
        showGrid = arg.lower() == "true"
    elif opt in ("-l", "--listen"):
        listenInput = arg.lower() == "true"
    elif opt in ("-e", "--export"):
        exportVideo = arg.lower() == "true"

W, H      = 720, 720
SIZE      = (W, H)
RW, RH    = W // 2, H // 2

FFMPEG_BIN = "ffmpeg"  # for Windows ffmpeg.exe
command = [
    FFMPEG_BIN,
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{W}x{H}",
    "-pix_fmt", "rgb32",
    "-r", "30",
    "-i", "-",
    "-an",
    "-b:v", "20M",
    "-q", "2",
    "my_output_videofile.avi",
]
pipe = sp.Popen(command, stdin=sp.PIPE) if exportVideo else None

DOT1COLOR = (63, 255, 191)
DOT2COLOR = (15, 127, 47)
DOT3COLOR = (11, 95, 35)
DOT4COLOR = (7, 31, 23)
DOT5COLOR = (3, 23, 11)
DOT6COLOR = (1, 15, 5)
DOT7COLOR = (0, 7, 3)
GRIDCOLOR = (0, 31, 63)
BGCOLOR   = (0, 63, 91)

FPS        = 30
SUBFRAMES  = 1
DOTALPHA   = 23

try:
    wro = wave.open(musix)
except FileNotFoundError:
    print("\nCould not open the WAV file.\n"
          "For example, you can download beams_4ch.wav from:\n"
          "http://luis.net/projects/scope/beams_4ch.wav\n")
    sys.exit(1)

SAMPLINGRATE   = wro.getframerate()
READ_LENGTH    = SAMPLINGRATE // FPS // SUBFRAMES
READ_LENGTH_QUAD = READ_LENGTH * 4
NFRAMES        = wro.getnframes()
NCHANNELS      = wro.getnchannels()
WIDTH          = wro.getsampwidth()

print(helpText)
print(f"\nSampling rate   : {SAMPLINGRATE} Hz"
      f"\nSamples/frame   : {READ_LENGTH}"
      f"\nChannels        : {NCHANNELS}"
      f"\nSample width    : {WIDTH} bytes\n")

if listenInput:
    print(f"Loading sound: {musix}")
    pa     = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(WIDTH),
                     channels=min(2, NCHANNELS),
                     rate=SAMPLINGRATE,
                     output=True,
                     frames_per_buffer=READ_LENGTH)

pygame.init()
screen = pygame.display.set_mode(SIZE, pygame.HWSURFACE | pygame.ASYNCBLIT)
pygame.display.set_caption(app_title)
clock = pygame.time.Clock()
fade = pygame.Surface(SIZE)
fade.set_alpha(128)      # decrease/increase for longer/shorter tail
fade.fill((0, 0, 0))

dot = pygame.Surface((7, 7))
dot.set_alpha(DOTALPHA)
dot.fill(BGCOLOR)
dot.fill(DOT7COLOR, pygame.Rect(0, 0, 7, 7))
dot.fill(DOT6COLOR, pygame.Rect(1, 0, 5, 7))
dot.fill(DOT6COLOR, pygame.Rect(0, 1, 7, 5))
dot.fill(DOT5COLOR, pygame.Rect(1, 1, 5, 5))
dot.fill(DOT4COLOR, pygame.Rect(2, 1, 3, 5))
dot.fill(DOT4COLOR, pygame.Rect(1, 2, 5, 3))
dot.fill(DOT3COLOR, pygame.Rect(2, 2, 3, 3))
dot.fill(DOT2COLOR, pygame.Rect(3, 2, 1, 3))
dot.fill(DOT2COLOR, pygame.Rect(2, 3, 3, 1))
dot.fill(DOT1COLOR, pygame.Rect(3, 3, 1, 1))

grid = pygame.Surface(SIZE, pygame.SRCALPHA)
grid.fill(BGCOLOR if showGrid else (0, 0, 0, 0))

if showGrid:
    for x in range(10):
        pygame.draw.line(grid, GRIDCOLOR, (x * W // 10, 0), (x * W // 10, H))
        pygame.draw.line(grid, GRIDCOLOR, (0, x * H // 10), (W, x * H // 10))

    pygame.draw.line(grid, GRIDCOLOR, (RW, 0), (RW, H), 3)
    pygame.draw.line(grid, GRIDCOLOR, (0, RH), (W, RH), 3)

    for x in range(W // 4):
        pygame.draw.line(grid, GRIDCOLOR,
                         (x * W // 128, RH - 3), (x * W // 128, RH + 3))
        pygame.draw.line(grid, GRIDCOLOR,
                         (RW - 3, x * H // 128), (RW + 3, x * H // 128))

frames    = wro.readframes(READ_LENGTH)
framelen  = len(frames)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    screen.blit(fade, (0, 0))
    if showGrid:
            screen.blit(grid, (0, 0))

    newdata = bytearray()
    ii = 4

    for i in range(0, READ_LENGTH_QUAD, 4):
        if i >= framelen:
            pygame.quit(); sys.exit()

        if (i & 4) == 0:
            r = struct.unpack('<hh', frames[i:i + 4])
            x = int((r[1] * W >> 16) + RW)
            y = int((-r[0] * H >> 16) + RH)
            if exportVideo:
                y, x = x, y
            screen.blit(dot, (x, y), None, pygame.BLEND_ADD)

        if (i & 2) == 0 and listenInput:
            newdata += frames[ii:ii + 4]
            ii += NCHANNELS * 2

    if listenInput:
        stream.write(bytes(newdata), exception_on_underflow=False)

    pygame.display.flip()

    if exportVideo and pipe:
        img = surfarray.array2d(screen)
        pipe.stdin.write(img.tobytes())

    frames   = wro.readframes(READ_LENGTH)
    framelen = len(frames)
    clock.tick_busy_loop(FPS)

    if framelen == 0:
        break

if listenInput:
    stream.stop_stream()
    stream.close()
    pa.terminate()
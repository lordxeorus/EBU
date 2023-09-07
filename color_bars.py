"""
Script by kirill_maker for generating EBU Color bars test pattern with 1KHz sine L/R signal.

Requires:

Python3, open-cv, pyaudio, numpy

Ubuntu 23.04 installation:

sudo apt install python3-full

pip install opencv-python --break-system-packages

sudo apt-get install portaudio19-dev

pip install --upgrade pip setuptools --break-system-packages
pip install pyaudio --break-system-packages

Controls:
Esc or q - exit
p - PAL/SECAM
n - NTSC
f - Fullscreen
"""

import cv2
import numpy as np
import pyaudio
import math
import struct

# Define video parameters for PAL, NTSC, and SECAM
video_presets = {
    'p': {'width': 720, 'height': 576, 'fps': 25.0},  # PAL/SECAM
    'n': {'width': 720, 'height': 480, 'fps': 29.97},  # NTSC
}

current_preset = 'p'

# Function to update the video resolution and frame rate based on the selected preset
def update_video_params(preset):
    global width, height, fps
    width = video_presets[preset]['width']
    height = video_presets[preset]['height']
    fps = video_presets[preset]['fps']
    cv2.resizeWindow('EBU Color Bars', width, height)

# Function to toggle fullscreen mode
def toggle_fullscreen():
    global is_fullscreen
    if is_fullscreen:
        cv2.setWindowProperty('EBU Color Bars', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    else:
        cv2.setWindowProperty('EBU Color Bars', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    is_fullscreen = not is_fullscreen

# Function to change the video preset and update parameters
def change_preset(preset_key):
    if preset_key in video_presets:
        current_preset = preset_key
        update_video_params(current_preset)

cv2.namedWindow('EBU Color Bars', cv2.WND_PROP_FULLSCREEN | cv2.WINDOW_GUI_NORMAL)
cv2.setWindowProperty('EBU Color Bars', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Initialize video parameters
update_video_params(current_preset)

# Create the EBU color bars pattern
bars = np.zeros((height, width, 3), dtype=np.uint8)

# Define RGB background color (black)
background_color = (0, 0, 0)

# Fill the entire image with the background color
bars[:, :, :] = background_color

# Define RGB color values
color_values = [
    (255, 255, 255),  # White
    (255, 255, 0),    # Yellow
    (0, 255, 255),    # Cyan
    (0, 255, 0),      # Green
    (255, 0, 255),    # Magenta
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 0, 0),        # Black
]

# Fill the color bars pattern vertically with RGB values
bar_width = width // 8
for i, (R, G, B) in enumerate(color_values):
    color = (B, G, R)  # OpenCV uses BGR instead of RGB
    bars[:, i * bar_width:(i + 1) * bar_width, :] = color

# Create an audio tone parameters
audio_sample_rate = 44100  # Audio sample rate (Hz)
audio_frequency = 1000  # 1 kHz audio tone

# Create stereo audio data with the same frequency for left and right channels
audio_data = []
for i in range(0, int(audio_sample_rate)):
    value = 32767 * math.sin(2.0 * math.pi * audio_frequency * i / audio_sample_rate)
    packed_value = struct.pack('h', int(value))
    audio_data.extend([packed_value, packed_value])  # Same value for both channels

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a stereo audio stream
audio_stream = audio.open(
    format=pyaudio.paInt16,
    channels=2,
    rate=audio_sample_rate,
    output=True
)

is_fullscreen = True

# Play the stereo audio and display the pattern until the window is closed
while True:
    cv2.imshow('EBU Color Bars', bars)
    audio_stream.write(b''.join(audio_data))

    # Check for key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # 'q' or 'Esc' key to exit
        break
    elif key == ord('f'):
        toggle_fullscreen()
    elif chr(key) in video_presets:
        change_preset(chr(key))

    # Check if the window was closed
    if cv2.getWindowProperty('EBU Color Bars', cv2.WND_PROP_VISIBLE) < 1:
        break

# Release resources
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
cv2.destroyAllWindows()

import configparser
import os
from tkinter.font import Font

# Network settings
DEFAULT_NETWORK = "127.0.0.1", 8000

config = configparser.ConfigParser()
if not os.path.exists('config.ini'):
    print('config.ini not found, creating with default settings.')
    config['NETWORK'] = {
        'RX_IP': DEFAULT_NETWORK[0],
        'RX_PORT': int(DEFAULT_NETWORK[1]),
        'TX_IP': DEFAULT_NETWORK[0],
        'TX_PORT': int(DEFAULT_NETWORK[1])
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
else:
    # Read the existing config file
    config.read('config.ini')

SERVER_ADDRESS = config.get('NETWORK', 'RX_IP'), int(config.get('NETWORK', 'RX_PORT'))

# GUI defaults
FOREGROUND = "#FCFCFA"
BACKGROUND = "#2D2A2E"
DEFAULT_FONT = Font(family="Source Code Pro", size=12)

# Timecode settings
FPS = 24


def change_FPS(new_fps):
    global FPS
    FPS = new_fps

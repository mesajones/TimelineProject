import configparser
import os


# Network settings
DEFAULT_NETWORK = "127.0.0.1", 53000, "127.0.0.1", 54000

config = configparser.ConfigParser()
if not os.path.exists('config.ini'):
    print('config.ini not found, creating with default settings.')
    config['NETWORK'] = {
        'QLAB_IP': DEFAULT_NETWORK[0],
        'QLAB_PORT': int(DEFAULT_NETWORK[1]),
        'EOS_IP': DEFAULT_NETWORK[2],
        'EOS_PORT': int(DEFAULT_NETWORK[3])
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
else:
    # Read the existing config file
    config.read('config.ini')

QLAB_ADDRESS = config.get('NETWORK', 'QLAB_IP'), int(config.get('NETWORK', 'QLAB_PORT'))
EOS_ADDRESS = config.get('NETWORK', 'EOS_IP'), int(config.get('NETWORK', 'EOS_PORT'))

# GUI defaults
FOREGROUND = "#D9D9D7"
BACKGROUND = "#2D2A2E"
HALF_ACCENT = "#38353A"
ACCENT = "#454147"
DEFAULT_FONT = "Spot Mono"

GREEN = "#A9DC76"
BLUE = "#78DCE8"
ORANGE = "#FF6188"

# Timecode settings
TIMECODE_FPS = 30


def change_fps(new_fps):
    global TIMECODE_FPS
    TIMECODE_FPS = new_fps

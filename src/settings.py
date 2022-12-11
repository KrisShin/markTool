from copy import deepcopy
from random import randint
import socket

WINDOW_TITLE = 'Mark Tool'
WINDOW_POSITION_X = 300
WINDOW_POSITION_Y = 300
WINDOW_POSITION = (WINDOW_POSITION_X, WINDOW_POSITION_Y)
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

TABLE_FILE_ROW_SPAN = 10
TABLE_FILE_COLUMN_SPAN = 20
TABLE_RULE_ROW_SPAN = 5
TABLE_RULE_COLUMN_SPAN = 8

TABLE_FILE_DEFAULT_HEADER = ['file name', 'score', 'total']
TABLE_FILE_HEADER = deepcopy(TABLE_FILE_DEFAULT_HEADER)
TABLE_RULE_HEADER = ['rule', 'weight']
RULES = {}

EDITABLE = True

SERVER_PORT = 43804  # randint(41027, 45960)
_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_socket.connect(("8.8.8.8", 80))
SERVER_HOST = _socket.getsockname()[0]
BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
WORKS = {}

SERVER_ALLOWED = False
SERVER_THREAD = None

VIDEO_EXTS = ['.mp4', '.3gp', '.flv']
IMAGE_EXTS = ['.jpg', '.jpeg', 'png']
TEXT_EXTS = ['.txt', '.md']

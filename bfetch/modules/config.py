import os

PROJ_DIR = os.getenv("BFETCH")

assert PROJ_DIR is not None, "No download folder configured"

CODE_DIR = PROJ_DIR + "/bfetch"

PATH_TO_CHROMEDRIVER = PROJ_DIR + '/chromedriver'

DATA_DIR = PROJ_DIR + "/data"

DOWNLOAD_PATH = PROJ_DIR + "/downloads"

# Default speed
SPEED = 2

# Time in seconds after which file download times out.
DOWNLOAD_TIMEOUT = 30

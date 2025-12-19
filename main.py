import sys

DIRECTORY = r"C:\Users\user\Documents\maya\maya_version\scripts\LimbRigging"


sys.path.append(DIRECTORY)

import importlib

import UI
importlib.reload(UI)
import library
importlib.reload(library)
import LimbClass
importlib.reload(LimbClass)
import bendy_limbs
importlib.reload(bendy_limbs)
import modules
importlib.reload(modules)


from UI import load_ui
from library import *
from typing import *

window_name = "LimbRiggingTool"
load_ui(window_name)
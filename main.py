import sys

DIRECTORY = r"C:\Users\manon\Documents\maya\scripts\LimbRigging"

sys.path.append(DIRECTORY)

import importlib

import UI
importlib.reload(UI)
import lib
importlib.reload(lib)
import LimbClass
importlib.reload(LimbClass)


from UI import load_ui
from lib import *

import maya.cmds as cmds
import functools
from typing import *

window_name = "LimbRiggingTool"
load_ui(window_name)
import sys

DIRECTORY = r"C:\Users\manon\Documents\maya\scripts\LimbRigging"

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


from UI import load_ui
from library import *

import maya.cmds as cmds
import functools
from typing import *

window_name = "LimbRiggingTool"
load_ui(window_name)
import maya.cmds as cmds
import functools
from typing import *

from library import *
from LimbClass import *


def toggle_visibility_callback(child_layout:str, *args):
    print(f"Showing {child_layout} !")
    cmds.rowLayout(child_layout, e=1, vis=True)
    
def toggle_invisibility_callback(child_layout:str, *args):
    print(f"Hiding {child_layout} !")
    cmds.rowLayout(child_layout, e=1, vis=False)

def create_invisible_separator(
    parent: str, isHorizontal: Optional[bool] = True, length: Optional[int] = None
):

    if length == None:
        cmds.separator(st="none", parent=parent, h=isHorizontal)
    else:
        cmds.separator(st="none", w=length, parent=parent, h=isHorizontal,)

def load_textfield_callback(textfield:str, *args):

    selection = get_selection()

    if len(selection)!= 1:
        error_msg("Please, select only 1 object.")

    to_load_txt:str = selection[0]
    cmds.textFieldGrp(textfield, e=True, tx=to_load_txt)

def load_ui(window_name: str):

    print("Loading...")

    # If the window exists, delete it
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name, window=True)
        print("Previous Window deleted")

    # Creates a window that fits around its children
    cmds.window(
        window_name,
        title=window_name,
        sizeable=False, rtf=True)

    # Use a colomn Layout
    parent_layout = cmds.columnLayout(
        adjustableColumn=True, rowSpacing=5
    )
    
    add_ui(parent_layout)

    # Parent the window to the main maya window
    cmds.setParent("..")

    # Show the window
    cmds.showWindow(window_name)

def add_ui(parent_layout:str):

    for i in range(3):
        create_invisible_separator(parent=parent_layout)

    # Text Fields

    cmds.textFieldButtonGrp(
        "txt_joint_root",
        parent=parent_layout,
        eb=True,
        pht="Root Joint",
        bl="Load",
        ad2=1,
        bc=functools.partial(load_textfield_callback, "txt_joint_root"))

    cmds.textFieldButtonGrp(
        "txt_controller_switch",
        parent=parent_layout,
        eb=True,
        pht="Switch Control",
        bl="Load",
        ad2=1,
        bc=functools.partial(load_textfield_callback, "txt_controller_switch"))
    
     # Limb Type Radio

    limb_type_layout = cmds.rowLayout("limb_type_layout", nc=2)
    cmds.radioCollection("limb_type_radiocollection", parent=limb_type_layout)
    cmds.radioButton("rad_limb_biped", l="Biped Limb", w=140, sl=True)
    cmds.radioButton("rad_limb_quadruped", l="Quadruped Limb", en=False)

    # Limb Position Options

    biped_layout = "opt_biped_layout"
    quadruped_layout = "opt_quadrued_layout"

    cmds.rowLayout(biped_layout, nc=2, ad2=2, parent = parent_layout)

    cmds.radioCollection("limb_type_position_biped_radiocollection", parent=biped_layout)
    cmds.radioButton("rad_limb_biped_arm", l="Arm", w=140, sl=True)
    cmds.radioButton("rad_limb_biped_leg", l="Leg")

    cmds.rowLayout(quadruped_layout, nc=2, ad2=2, vis=False,  parent = parent_layout)

    cmds.radioCollection("limb_type_position_quadrued_radiocollection", parent=quadruped_layout)
    cmds.radioButton("rad_limb_quadruped_front", l="Front", w=140, sl=True)
    cmds.radioButton("rad_limb_quadruped_rear", l="Rear")

    # Visibility Options

    cmds.radioButton("rad_limb_biped",e=True, onc=functools.partial(toggle_visibility_callback,biped_layout))
    cmds.radioButton("rad_limb_biped",e=True, ofc=functools.partial(toggle_invisibility_callback,biped_layout))
    cmds.radioButton("rad_limb_quadruped",e=True, onc=functools.partial(toggle_visibility_callback,quadruped_layout))
    cmds.radioButton("rad_limb_quadruped",e=True, ofc=functools.partial(toggle_invisibility_callback,quadruped_layout))


    cmds.checkBox("ckb_limb_stretch", l="Stretch System", parent = parent_layout)

    
    # Buttons Callbacks

    cmds.button("btn_limb_hierachy", l="Create Hierachies", parent=parent_layout, command = duplicate_hierarchies_callback)
    cmds.button("btn_limb_blend", l="Pair Blend Hierachies", parent=parent_layout, command= pair_blend_callback)

    # Controls

    cmds.checkBox("ckb_better_pole", l="Better pole vector", parent=parent_layout)
    cmds.button("btn_limb_controls", l="Add Controllers",parent=parent_layout, command = add_controls_callback)

    biped_options ="biped_command_layout"
    cmds.rowLayout(biped_options, nc=2,ad2=2, parent=parent_layout)

    cmds.button("btn_limb_hand", l="Add FK Hand",parent=biped_options,w=140 ,command = add_hand_controls_callback)
    cmds.button("btn_limb_foot_roll", l="Add IK foot roll",parent=biped_options, command = print)

    cmds.button("btn_limb_ribbon", l="Add Ribbon to Limb",parent=parent_layout, command = print)


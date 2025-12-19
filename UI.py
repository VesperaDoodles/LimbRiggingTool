import maya.cmds as cmds
import functools
from typing import *

from library import *
from LimbClass import *
from bendy_limbs import create_bendy_limb


def toggle_visibility_callback(child_layout: str, *args):
    cmds.rowLayout(child_layout, e=1, vis=True)


def toggle_invisibility_callback(child_layout: str, *args):
    cmds.rowLayout(child_layout, e=1, vis=False)


def create_invisible_separator(
    parent: str, isHorizontal: Optional[bool] = True, length: Optional[int] = None
):

    if length == None:
        cmds.separator(st="none", parent=parent, h=isHorizontal)
    else:
        cmds.separator(
            st="none",
            w=length,
            parent=parent,
            h=isHorizontal,
        )


def load_textfield_callback(textfield: str, *args):

    selection = get_selection()

    if len(selection) != 1:
        raise ValueError ("Please, select only 1 object.")

    to_load_txt: str = selection[0]
    cmds.textFieldGrp(textfield, e=True, tx=to_load_txt)


def load_ui(window_name: str):

    print("Loading...")

    # If the window exists, delete it
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name, window=True)
        print("Previous Window deleted")

    # Creates a window that fits around its children
    cmds.window(window_name, title=window_name, sizeable=False, rtf=True)

    # Use a colomn Layout
    margins_layout = cmds.frameLayout(mw= 5, mh=5, l="Limb Rigging", lv=False )

    parent_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, p=margins_layout)

    add_ui(parent_layout)

    # Parent the window to the main maya window
    cmds.setParent("..")

    # Show the window
    cmds.showWindow(window_name)


def add_ui(parent_layout: str):

    # Text Fields

    cmds.floatFieldGrp("ff_limb_scale", p=parent_layout, l="Scale : ", v1=1.0, ad2=2, cal=[1, "left"], cw=[1, 50])

    cmds.text(p=parent_layout, l= "Root Joint", al="left")

    cmds.textFieldButtonGrp(
        "txt_joint_root",
        parent=parent_layout,
        eb=True,
        pht="SK_root_side",
        bl="Load",
        ad2=1,
        bc=functools.partial(load_textfield_callback, "txt_joint_root"),
    )

    cmds.text(p=parent_layout, l= "Switch Controller", al="left")

    cmds.textFieldButtonGrp(
        "txt_controller_switch",
        parent=parent_layout,
        eb=True,
        pht="CTRL_switch_limb_side",
        bl="Load",
        ad2=1,
        bc=functools.partial(load_textfield_callback, "txt_controller_switch"),
    )

    # Limb Type Radio

    limb_type_layout = cmds.rowLayout("limb_type_layout", nc=2)
    cmds.radioCollection("limb_type_radiocollection", parent=limb_type_layout)
    cmds.radioButton("rad_limb_biped", l="Biped Limb", w=140, sl=True)
    cmds.radioButton("rad_limb_quadruped", l="Quadruped Limb", en=False)

    # Limb Position Options

    biped_layout = "opt_biped_layout"
    quadruped_layout = "opt_quadrued_layout"

    cmds.rowLayout(biped_layout, nc=2, ad2=2, parent=parent_layout)

    cmds.radioCollection(
        "limb_type_position_biped_radiocollection", parent=biped_layout
    )
    cmds.radioButton("rad_limb_biped_arm", l="Arm", w=140, sl=True)
    cmds.radioButton("rad_limb_biped_leg", l="Leg")

    cmds.rowLayout(quadruped_layout, nc=2, ad2=2, vis=False, parent=parent_layout)

    cmds.radioCollection(
        "limb_type_position_quadrued_radiocollection", parent=quadruped_layout
    )
    cmds.radioButton("rad_limb_quadruped_front", l="Front", w=140, sl=True)
    cmds.radioButton("rad_limb_quadruped_rear", l="Rear")

    # Visibility Options

    cmds.radioButton(
        "rad_limb_biped",
        e=True,
        onc=functools.partial(toggle_visibility_callback, biped_layout),
    )
    cmds.radioButton(
        "rad_limb_biped",
        e=True,
        ofc=functools.partial(toggle_invisibility_callback, biped_layout),
    )
    cmds.radioButton(
        "rad_limb_quadruped",
        e=True,
        onc=functools.partial(toggle_visibility_callback, quadruped_layout),
    )
    cmds.radioButton(
        "rad_limb_quadruped",
        e=True,
        ofc=functools.partial(toggle_invisibility_callback, quadruped_layout),
    )

    cmds.checkBox("ckb_limb_stretch", l="Stretch System", parent=parent_layout)

    # Buttons Callbacks

    cmds.button(
        "btn_limb_hierachy",
        l="Create Blended Hierachies",
        parent=parent_layout,
        command=duplicate_hierarchies_callback,
    )

    # Controls

    cmds.checkBox("ckb_better_pole", l="Better pole vector", parent=parent_layout)
    cmds.button(
        "btn_limb_controls",
        l="Add Controllers",
        parent=parent_layout,
        command=add_controls_callback,
    )

    reverse_foot = "reverse_foot_layout"
    cmds.rowLayout(reverse_foot, p=parent_layout, vis=False)

    cmds.textFieldButtonGrp(
        "txt_foot_root",
        parent=reverse_foot,
        eb=True,
        pht="Reverse Foot Root",
        bl="Load",
        ad2=1,
        bc=functools.partial(load_textfield_callback, "txt_foot_root"),
    )

    cmds.radioButton(
        "rad_limb_biped_leg",
        e=True,
        onc=functools.partial(toggle_visibility_callback, reverse_foot),
    )
    cmds.radioButton(
        "rad_limb_biped_leg",
        e=True,
        ofc=functools.partial(toggle_invisibility_callback, reverse_foot),
    )

    biped_options = "biped_command_layout"
    cmds.rowLayout(biped_options, nc=2, ad2=2, parent=parent_layout)

    cmds.button(
        "btn_limb_hand",
        l="Add FK Hand",
        parent=biped_options,
        w=140,
        command=hand_attr_value_window,
    )
    cmds.button(
        "btn_limb_foot_roll",
        l="Add IK foot roll",
        parent=biped_options,
        command=add_foot_roll_callback,
    )

    cmds.button(
        "btn_limb_ribbon",
        l="Add Ribbon to Limb",
        parent=parent_layout,
        command=create_bendy_limb,
        en=True,
    )


def hand_attr_value_window(*args):

    window_name = "UpdateAttibutes"

    # If the window exists, delete it
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name, window=True)
        print("Previous Window deleted")

    # Creates a window that fits around its children
    cmds.window(window_name, title=window_name, sizeable=False, rtf=True)

    # Use a colomn Layout
    parent_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

    cmds.floatSliderGrp(
        "sld_curl",
        l="Curl Multiplier",
        p=parent_layout,
        s=5,
        f=True,
        v=1,
        cc=update_curl_attributes_callback,
        ad3=1,
    )
    cmds.floatSliderGrp(
        "sld_spread",
        l="Spread Multiplier",
        p=parent_layout,
        s=5,
        f=True,
        v=1,
        cc=update_spread_attributes_callback,
        ad3=1,
    )
    cmds.floatSliderGrp(
        "sld_orient",
        l="Orient Multiplier",
        p=parent_layout,
        s=5,
        f=True,
        v=1,
        cc=update_orient_attributes_callback,
        ad3=1,
    )

    # Parent the window to the main maya window
    cmds.setParent("..")

    add_hand_controls_callback()

    # Show the window
    cmds.showWindow(window_name)
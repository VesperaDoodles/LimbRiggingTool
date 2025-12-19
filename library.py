import maya.cmds as cmds
import maya.api.OpenMaya as om
import functools
from typing import *


controllers_library: Dict[str, List[Tuple[float, float, float]]] = {
    "square": [(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0), (1, 1, 0)],
    "triangle": [(1, -1, 0), (-1, -1, 0), (0, 1, 0), (1, -1, 0)],
    "cross": [
        (0.3, 1, 0),
        (-0.3, 1, 0),
        (-0.3, 0.3, 0),
        (-1, 0.3, 0),
        (-1, -0.3, 0),
        (-0.3, -0.3, 0),
        (-0.3, -1, 0),
        (0.3, -1, 0),
        (0.3, -0.3, 0),
        (1, -0.3, 0),
        (1, 0.3, 0),
        (0.3, 0.3, 0),
        (0.3, 1, 0),
    ],
    "main": [
        (0.3, 0, 1),
        (0.5, 0, 1),
        (0.0, 0.0, 1.5),
        (-0.5, 0.0, 1.0),
        (-0.3, 0.0, 1.0),
        (-0.3, 0.0, 0.3),
        (-1.0, 0.0, 0.3),
        (-1.0, 0.0, 0.5),
        (-1.5, 0.0, 0.0),
        (-1.0, 0.0, -0.5),
        (-1.0, 0.0, -0.3),
        (-0.3, 0.0, -0.3),
        (-0.3, 0.0, -1.0),
        (-0.5, 0.0, -1.0),
        (0.0, 0.0, -1.5),
        (0.5, 0.0, -1.0),
        (0.3, 0.0, -1.0),
        (0.3, 0.0, -0.3),
        (1.0, 0.0, -0.3),
        (1.0, 0.0, -0.5),
        (1.5, 0.0, 0.0),
        (1.0, 0.0, 0.5),
        (1.0, 0.0, 0.3),
        (0.3, 0.0, 0.3),
        (0.3, 0.0, 1.0),
    ],
    "pointer": [
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.3, 1.3, 0.0),
        (0.0, 1.6, 0.0),
        (-0.3, 1.3, 0.0),
        (0.0, 1.0, 0.0),
    ],
    "pole": [
        (0.0, 0.0, 1.2),
        (0.0, -1.2, -1.2),
        (0.0, 1.2, -1.2),
        (0.0, 0.0, 1.2),
        (-1.2, 0.0, -1.2),
        (1.2, 0.0, -1.2),
        (0.0, 0.0, 1.2),
    ],
    "arrow": [
        (0.3, 0, 0),
        (-0.3, 0, 0),
        (-0.3, 1, 0),
        (-0.5, 1, 0),
        (0, 1.5, 0),
        (0.5, 1, 0),
        (0.3, 1, 0),
        (0.3, 0, 0),
    ],
    "doubleArrow": [
        (0.3, 1.0, 0.0),
        (0.5, 1.0, 0.0),
        (0.0, 1.5, 0.0),
        (-0.5, 1.0, 0.0),
        (-0.3, 1.0, 0.0),
        (-0.3, -1.0, 0.0),
        (-0.5, -1.0, 0.0),
        (0.0, -1.5, 0.0),
        (0.5, -1.0, 0.0),
        (0.3, -1.0, 0.0),
        (0.3, 1.0, 0.0),
    ],
    "box": [
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0),
        (1.0, 1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0, -1.0, 1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (1.0, 1.0, 1.0),
        (1.0, 1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
    ],
    "joint": [
        (0.0, 1.0, 0.0),
        (0.0, 0.92388, 0.382683),
        (0.0, 0.707107, 0.707107),
        (0.0, 0.382683, 0.92388),
        (0.0, 0.0, 1.0),
        (0.0, -0.382683, 0.92388),
        (0.0, -0.707107, 0.707107),
        (0.0, -0.92388, 0.382683),
        (0.0, -1.0, 0.0),
        (0.0, -0.92388, -0.382683),
        (0.0, -0.707107, -0.707107),
        (0.0, -0.382683, -0.92388),
        (0.0, 0.0, -1.0),
        (0.0, 0.382683, -0.92388),
        (0.0, 0.707107, -0.707107),
        (0.0, 0.92388, -0.382683),
        (0.0, 1.0, 0.0),
        (0.382683, 0.92388, 0.0),
        (0.707107, 0.707107, 0.0),
        (0.92388, 0.382683, 0.0),
        (1.0, 0.0, 0.0),
        (0.92388, -0.382683, 0.0),
        (0.707107, -0.707107, 0.0),
        (0.382683, -0.92388, 0.0),
        (0.0, -1.0, 0.0),
        (-0.382683, -0.92388, 0.0),
        (-0.707107, -0.707107, 0.0),
        (-0.92388, -0.382683, 0.0),
        (-1.0, 0.0, 0.0),
        (-0.92388, 0.382683, 0.0),
        (-0.707107, 0.707107, 0.0),
        (-0.382683, 0.92388, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.92388, -0.382683),
        (0.0, 0.707107, -0.707107),
        (0.0, 0.382683, -0.92388),
        (0.0, 0.0, -1.0),
        (-0.382683, 0.0, -0.92388),
        (-0.707107, 0.0, -0.707107),
        (-0.92388, 0.0, -0.382683),
        (-1.0, 0.0, 0.0),
        (-0.92388, 0.0, 0.382683),
        (-0.707107, 0.0, 0.707107),
        (-0.382683, 0.0, 0.92388),
        (0.0, 0.0, 1.0),
        (0.382683, 0.0, 0.92388),
        (0.707107, 0.0, 0.707107),
        (0.92388, 0.0, 0.382683),
        (1.0, 0.0, 0.0),
        (0.92388, 0.0, -0.382683),
        (0.707107, 0.0, -0.707107),
        (0.382683, 0.0, -0.92388),
        (0.0, 0.0, -1.0),
    ],
    "switch": [
        (-0.1033, 1.0115, 0.0),
        (0.1033, 1.0115, 0.0),
        (0.2066, 0.8315, 0.0),
        (0.4418, 0.7341, 0.0),
        (0.6422, 0.7883, 0.0),
        (0.7883, 0.6422, 0.0),
        (0.7341, 0.4418, 0.0),
        (0.8315, 0.2066, 0.0),
        (1.0115, 0.1033, 0.0),
        (1.0115, -0.1033, 0.0),
        (0.8315, -0.2066, 0.0),
        (0.7341, -0.4418, 0.0),
        (0.7883, -0.6422, 0.0),
        (0.6422, -0.7883, 0.0),
        (0.4418, -0.7341, 0.0),
        (0.2066, -0.8315, 0.0),
        (0.1033, -1.0115, 0.0),
        (-0.1033, -1.0115, 0.0),
        (-0.2066, -0.8315, 0.0),
        (-0.4418, -0.7341, 0.0),
        (-0.6422, -0.7883, 0.0),
        (-0.7883, -0.6422, 0.0),
        (-0.7341, -0.4418, 0.0),
        (-0.8315, -0.2066, 0.0),
        (-1.0115, -0.1033, 0.0),
        (-1.0115, 0.1033, 0.0),
        (-0.8315, 0.2066, 0.0),
        (-0.7341, 0.4418, 0.0),
        (-0.7883, 0.6422, 0.0),
        (-0.6422, 0.7883, 0.0),
        (-0.4418, 0.7341, 0.0),
        (-0.2066, 0.8315, 0.0),
        (-0.1033, 1.0115, 0.0),
    ],
}

class BipedLimb:
    Arm = "arm"
    Leg = "leg"

class QuadrupedLimb:
    Forelimb = "forelimb"
    Hindlimb = "hindlimb"

class WarningManager:
    def __init__(self):
        pass

    def __enter__(self):
        print("Unsuppressing Warnings now")
        cmds.scriptEditorInfo(suppressWarnings=0,suppressInfo=0,se=0)
    
    def __exit__(self, type, value, traceback):
        print("Suppressing Warnings now")
        cmds.scriptEditorInfo(suppressWarnings=1,suppressInfo=1,se=1)

def suppress_warnings():
    return WarningManager()

def get_selection(typ: Optional[str] = None):

    ###################################

        # Inputs - typ ( Optionnal ), str
        # Returns - List

        # Return the current selection, of specified type 

        ###################################

    if typ == None:
        selection: List[str] = cmds.ls(selection=True)
    else:
        selection: List[str] = cmds.ls(selection=True, typ=typ)

    return selection

def get_float_field(name:str):
    ###################################

    # Inputs - name, str
    # Returns - float

    # Returns the float text in the specified float field

    ###################################
    return float(cmds.floatFieldGrp(name, q=True, v1=True))


def get_loaded_text_field(name: str):
    ###################################

    # Inputs - name, str
    # Returns - str

    # Returns the loaded text in the specified text field

    ###################################
    return str(cmds.textFieldButtonGrp(name, q=True, tx=True))


def is_checked(name: str):
    ###################################
    # Inputs - name, str
    # Returns - bool
    # Checks whether a checkbox is checked.
    ###################################
    return bool(cmds.checkBox((name), query=True, value=True))


def radio_is_checked(name: str):
    ###################################
    # Inputs - name, str
    # Returns - bool
    # Checks whether a radio button is selected.
    ###################################
    return bool(cmds.radioButton((name), query=True, select=True))


def get_chosen_option(name: str):
    ###################################
    # Inputs - name, str
    # Returns - str
    # Retrieves the currently selected option from an option menu.
    ###################################
    return cmds.optionMenu((name), query=True, v=True)


def get_slider_field(name: str):
    ###################################
    # Inputs - name, str
    # Returns - float
    # Gets the current value of a float slider field.
    ###################################
    return float(cmds.floatSliderGrp(name, query=True, v=True))


def get_hierachy(root_joint: str):
    ###################################
    # Inputs - root_joint, str
    # Returns - List[str]
    # Retrieves the hierarchy of joints starting from the root joint.
    ###################################
    joint_hierarchy: List[str] = cmds.listRelatives(root_joint, ad=1)
    joint_hierarchy.append(root_joint)
    joint_hierarchy.reverse()
    return joint_hierarchy


def set_attr(obj: str, attr: str, *values, **kwargs):
    ###################################
    # Inputs - obj, str; attr, str; values, variadic; kwargs, dict
    # Returns - None
    # Sets the value of an attribute for a specified object.
    ###################################
    cmds.setAttr(f"{obj}.{attr}", *values, **kwargs)


def set_appearance(obj: str, red: float, green: float, blue: float):
    ###################################
    # Inputs - obj, str; red, float; green, float; blue, float
    # Returns - None
    # Changes the appearance of an object to specified RGB values.
    ###################################
    set_attr(obj, "overrideEnabled", 1)
    set_attr(obj, "overrideRGBColors", 1)
    set_attr(obj, "overrideColorRGB", red, green, blue)


def lock_transforms(object: str, to_lock:bool=True):
    ###################################
    # Inputs - object, str; to_lock, bool
    # Returns - None
    # Locks or Unlocks(and makes keyable) the translate, rotate, and scale attributes.
    ###################################

    for attr in ['translate', 'rotate', 'scale']:

        for axis in 'XYZ':

            attr_name = f"{object}.{attr}{axis}"

            # Lock (or Unlock) the attribute
            cmds.setAttr(attr_name, lock=to_lock)

            # Ensure it is keyable if unlocked
            cmds.setAttr(attr_name, keyable= not to_lock)


def connect_attr(input_obj: str, input_attr: str, output_obj: str, output_attr: str):
    ###################################
    # Inputs - input_obj, str; input_attr, str; output_obj, str; output_attr, str
    # Returns - None
    # Connects an attribute from one object to another.
    ###################################
    cmds.connectAttr(
        f"{input_obj}.{input_attr}", f"{output_obj}.{output_attr}", force=1
    )


def set_lineWidth(curve: str, width: float = 2, isShape: Optional[bool] = False):
    ###################################
    # Inputs - curve, str; width, float; isShape, bool
    # Returns - None
    # Sets the line width of a specified curve.
    ###################################
    
    if isShape or "Shape" in curve:
        cmds.setAttr(f"{curve}" + ".lineWidth", width, edit=True)
    else:
        curve = curve.split("|")[-1]
        shape = "|" + cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(f"{curve}{shape}" + ".lineWidth", width, edit=True)


def constraint(
    parent_obj: str,
    constrained_obj: str,
    translate_value: Optional[bool] = True,
    orient_value: Optional[bool] = True,
    scale_value: Optional[bool] = False,
    maintain_offset_value: Optional[bool] = False,
):
    ###################################
    # Inputs - parent_obj, str; constrained_obj, str;
    #          translate_value, bool; orient_value, bool;
    #          scale_value, bool; maintain_offset_value, bool
    # Returns - str or List[str]
    # Creates a constraint between two objects with specified options.
    ###################################

    constraint_name: str = None

    if translate_value and orient_value:
        constraint_name: str = cmds.parentConstraint(
            parent_obj, constrained_obj, mo=maintain_offset_value, w=1
        )
    else:
        if translate_value:
            constraint_name: str = cmds.pointConstraint(
                parent_obj, constrained_obj, mo=maintain_offset_value, w=1
            )
        elif orient_value:
            constraint_name: str = cmds.orientConstraint(
                parent_obj, constrained_obj, mo=maintain_offset_value, w=1
            )

    if scale_value:
        constraint_scale_name: str = cmds.scaleConstraint(
            parent_obj, constrained_obj, mo=maintain_offset_value, w=1
        )
        return [constraint_name, constraint_scale_name]

    return constraint_name
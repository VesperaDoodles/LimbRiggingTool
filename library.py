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
        (-4.0, -4.0, 4.0),
        (-4.0, 4.0, 4.0),
        (-4.0, 4.0, -4.0),
        (-4.0, -4.0, -4.0),
        (-4.0, -4.0, 4.0),
        (4.0, -4.0, 4.0),
        (4.0, 4.0, 4.0),
        (4.0, 4.0, -4.0),
        (4.0, -4.0, -4.0),
        (4.0, -4.0, 4.0),
        (-4.0, -4.0, 4.0),
        (-4.0, 4.0, 4.0),
        (4.0, 4.0, 4.0),
        (4.0, 4.0, -4.0),
        (-4.0, 4.0, -4.0),
        (-4.0, -4.0, -4.0),
        (4.0, -4.0, -4.0),
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


def error_msg(message) -> NoReturn:
    cmds.error(message)
    raise Exception("Should Never Happend")


def get_selection(typ: Optional[str] = None):

    if typ == None:
        selection: List[str] = cmds.ls(selection=True)
    else:
        selection: List[str] = cmds.ls(selection=True, typ=typ)

    return selection


def get_loaded_text_field(name: str):
    return str(cmds.textFieldButtonGrp(name, q=True, tx=True))


def is_checked(name: str):
    return bool(cmds.checkBox((name), query=True, value=True))


def radio_is_checked(name: str):
    return bool(cmds.radioButton((name), query=True, select=True))


def get_chosen_option(name: str):
    return cmds.optionMenu((name), query=True, v=True)


def get_slider_field(name: str):
    return float(cmds.floatSliderGrp(name, query=True, v=True))


def get_hierachy(root_joint: str):

    joint_hierarchy: List[str] = cmds.listRelatives(root_joint, ad=1)
    joint_hierarchy.append(root_joint)
    joint_hierarchy.reverse()

    return joint_hierarchy


def set_attr(obj: str, attr: str, *values, **kwargs):
    cmds.setAttr(f"{obj}.{attr}", *values, **kwargs)


def set_appearance(obj: str, red: float, green: float, blue: float):
    set_attr(obj, "overrideEnabled", 1)
    set_attr(obj, "overrideRGBColors", 1)
    set_attr(obj, "overrideColorRGB", red, green, blue)


def unlock_transforms(object:str):

    for attr in ['translate', 'rotate', 'scale']:
        for axis in 'XYZ':
            attr_name = f"{object}.{attr}{axis}"
            
            # Unlock the attribute
            if cmds.getAttr(attr_name, lock=True):
                cmds.setAttr(attr_name, lock=False)
            # Ensure it is keyable
            cmds.setAttr(attr_name, keyable=True)


def connect_attr(input_obj: str, input_attr: str, output_obj: str, output_attr: str):

    cmds.connectAttr(
        f"{input_obj}.{input_attr}", f"{output_obj}.{output_attr}", force=1
    )


def set_lineWidth(curve: str, width: float = 2, isShape: Optional[bool] = False):

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


def create_control_fk(jnt: str, side: str, radius: int = 8):

    # Creates a FK controler and an offset group to a joint
    ctrl = cmds.circle(
        c=(0, 0, 0),
        nr=(1, 0, 0),
        sw=360,
        r=radius,
        s=8,
        ch=False,
        n=jnt.replace("SK_JNT", "CTRL_FK"),
    )
    shape = cmds.listRelatives(ctrl, shapes=True)[0]

    # Creation of offset group
    offset = cmds.group(ctrl, n=jnt.replace("SK_JNT", "offset_FK"))

    # Modification of controlers appearance
    set_lineWidth(ctrl[0], 2)

    colors = {"L": (0, 0, 1), "R": (1, 0, 0)}
    if side in colors:
        color = colors[side]
    else:
        color = (1, 1, 0)

    set_appearance(shape, color[0], color[1], color[2])

    cmds.matchTransform(offset, jnt)


def calculate_pole_vector_position(
    shoulder_joint: str, elbow_joint: str, wrist_joint: str, offset: float = 20.0
):
    """
    Calculate the ideal position for a pole vector controller.

    Args:
        shoulder_joint (str): Name of the shoulder joint.
        elbow_joint (str): Name of the elbow joint.
        wrist_joint (str): Name of the wrist joint.
        offset (float): Distance to offset the pole vector along the calculated normal.

    Returns:
        tuple: World-space position of the pole vector.
    """

    shoulder_pos = om.MVector(cmds.xform(shoulder_joint, q=True, ws=True, t=True))
    elbow_pos = om.MVector(cmds.xform(elbow_joint, q=True, ws=True, t=True))
    wrist_pos = om.MVector(cmds.xform(wrist_joint, q=True, ws=True, t=True))

    # Calculate midpoint
    midpoint = (shoulder_pos + wrist_pos) * 0.5

    # Vector from midpoint to elbow
    mid_to_elbow = (elbow_pos - midpoint).normal()

    # Offset along this direction
    pole_vector_pos = elbow_pos + (mid_to_elbow * offset)
    return (pole_vector_pos.x, pole_vector_pos.y, pole_vector_pos.z)


def create_control_ik(
    joint_hierarchy: List[str],
    end_joint: str,
    side: str,
    end_control: str,
    pole_control: str,
    hock_control: Optional[str] = None,
    is_quad: Optional[bool] = False,
):

    end = cmds.curve(
        d=1,
        p=controllers_library["box"],
        k=list(range(len((controllers_library["box"])))),
        n=end_control,
    )
    shape = cmds.listRelatives(end, shapes=True)[0]

    pole = cmds.curve(
        d=1,
        p=controllers_library["joint"],
        k=list(range(len((controllers_library["joint"])))),
        n=pole_control,
    )
    shape_pole = cmds.listRelatives(pole, shapes=True)[0]

    # Colors according to chart
    colors = {"L": (0, 0.6, 1), "R": (1, 0, 0)}
    if side in colors:
        color = colors[side]
    else:
        color = (1, 1, 0)

    # Modification of controlers appearance
    set_appearance(shape, color[0], color[1], color[2])
    set_appearance(shape_pole, color[0], color[1], color[2])

    set_lineWidth(shape, 1.5)
    set_lineWidth(shape_pole, 1.5)

    if is_quad:

        hock_joint = cmds.listRelatives(end_joint, p=True)

        hock = cmds.curve(
            d=1,
            p=controllers_library["box"],
            k=list(range(len((controllers_library["box"])))),
            n=hock_control,
        )
        shape_hock = cmds.listRelatives(hock, shapes=True)[0]

        set_appearance(shape_hock, color[0], color[1], color[2])
        set_lineWidth(shape_hock, 1.5)

        offset_hock = cmds.group(hock, n=hock.replace("CTRL", "offset"))
        cmds.matchTransform(offset_hock, hock_joint, px=1, py=1, pz=1, rx=0, ry=0, rz=0)

    # Creation of offset groups
    offset_end = cmds.group(end, n=end_control.replace("CTRL", "offset"))
    cmds.matchTransform(offset_end, end_joint, pos=True, rot=True, piv=True)

    offset_pole = cmds.group(pole, n=pole_control.replace("CTRL", "offset"))
    position = calculate_pole_vector_position(
        joint_hierarchy[0], joint_hierarchy[1], joint_hierarchy[2]
    )

    cmds.setAttr(offset_pole + ".translateX", position[0])
    cmds.setAttr(offset_pole + ".translateY", position[1])
    cmds.setAttr(offset_pole + ".translateZ", position[2])


def parent_control_fk(joints_list: List[str], index: int):

    # Parents a controler's offset group to the correct controler
    offset = joints_list[index].replace("SK_JNT", "offset_FK")
    if index > 0:
        offset = joints_list[index].replace("SK_JNT", "offset_FK")
        ctrl_parent = joints_list[index - 1].replace("SK_JNT", "CTRL_FK")
        cmds.parent(offset, ctrl_parent)
    else:
        return offset


def stretch(
    joint_root, joint_hierarchy, suffix_name, ik_control, switch_ctrl, is_biped=True
):
    # Setup Stretch

    # Set up a measure distance node

    # Start Point is the root joint, end point the third joint in the hierachy
    start_point = cmds.xform(joint_root, query=True, translation=True, ws=True)
    if is_biped:
        last_joint_index = 2
    else:
        last_joint_index = 3

    end_point = cmds.xform(
        joint_hierarchy[last_joint_index], query=True, translation=True, ws=True
    )
    distance_node = cmds.distanceDimension(sp=start_point, ep=end_point)

    cmds.select(distance_node.replace("Shape", ""))
    cmds.rename("distance_" + suffix_name)
    distance_node = "distance_" + suffix_name

    cmds.select(cl=1)

    # Rename the newly created locators and rename them
    if cmds.objExists("locator1"):
        set_attr("locator1", "visibility", 0)
        if cmds.xform("locator1", query=True, translation=True, ws=True) == end_point:
            # If the locator is on the end joint, parent it to the IK control
            cmds.parent("locator1", ik_control)
            cmds.select("locator1")
            cmds.rename("loc_distance_end_" + suffix_name)

        elif (
            cmds.xform("locator1", query=True, translation=True, ws=True) == start_point
        ):
            # If the locator is on the root joint, constraint it to the root joint
            constraint(joint_root, "locator1", orient_value=False)
            cmds.select("locator1")
            cmds.rename("loc_distance_start_" + suffix_name)

    if cmds.objExists("locator2"):
        set_attr("locator2", "visibility", 0)
        if cmds.xform("locator2", query=True, translation=True, ws=True) == end_point:
            # If the locator is on the end joint, parent it to the IK control
            cmds.parent("locator2", ik_control)
            cmds.select("locator2")
            cmds.rename("loc_distance_end_" + suffix_name)

        elif (
            cmds.xform("locator2", query=True, translation=True, ws=True) == start_point
        ):
            # If the locator is on the root joint, constraint it to the root joint
            constraint(joint_root, "locator2", orient_value=False)
            cmds.select("locator2")
            cmds.rename("loc_distance_start_" + suffix_name)

    cmds.select(cl=1)

    # Create a float Math Node, a condition Node and a blendColors Node

    base_distance = cmds.getAttr(distance_node + ".distance")
    condition_node = "condition_stretch_" + suffix_name
    cmds.shadingNode("condition", n=condition_node, au=1)

    floatMath_node = "floatMath_stretch_" + suffix_name
    cmds.shadingNode("floatMath", n=floatMath_node, au=1)

    blendColors_node = "blendColors_stretch_" + suffix_name
    cmds.shadingNode("blendColors", n=blendColors_node, au=1)

    # Float Math Node
    cmds.connectAttr(
        distance_node + ".distance",
        floatMath_node + ".floatA",
        f=1,
    )
    set_attr(floatMath_node, "operation", 3)
    set_attr(floatMath_node, "floatB", base_distance)

    # Condition Node
    cmds.connectAttr(
        distance_node + ".distance",
        condition_node + ".firstTerm",
        f=1,
    )
    cmds.connectAttr(
        floatMath_node + ".outFloat",
        condition_node + ".colorIfTrue.colorIfTrueR",
        f=1,
    )
    set_attr(condition_node, "operation", 2)
    set_attr(condition_node, "secondTerm", base_distance)

    # BlendColors Node
    cmds.connectAttr(
        condition_node + ".outColor.outColorR",
        "blendColors_stretch_" + suffix_name + ".color1.color1R",
        f=1,
    )

    if not cmds.attributeQuery("stretch", ex=True, n=switch_ctrl):

        cmds.warning("No Stretch Attribute found, creating one")
        cmds.addAttr(switch_ctrl, ln="stretch", at="float", min=0, max=1, k=True)

    cmds.connectAttr(
        switch_ctrl + ".stretch",
        "blendColors_stretch_" + suffix_name + ".blender",
        f=1,
    )
    set_attr("blendColors_stretch_" + suffix_name, "color2.color2R", 1)

    # Connect the final output to scale X of the SK skeleton (except the last joint)

    for jnt in joint_hierarchy:

        if not jnt == joint_hierarchy[last_joint_index]:
            cmds.connectAttr(
                "blendColors_stretch_" + suffix_name + ".output.outputR",
                jnt + ".scaleX",
                f=1
            )
            cmds.connectAttr(
                "blendColors_stretch_" + suffix_name + ".output.outputR",
                jnt.replace("SK", "IK") + ".scaleX",
                f=1
            )
        else:
            break

    set_attr(distance_node, "visibility", 0)


def add_unbreakable_knees(
    pole_vector_ctrl: str, hierarchy: List[str], root_parent: str
):

    side = pole_vector_ctrl[-1]

    pole_grp = cmds.group(pole_vector_ctrl, n=f"grp_pole_flip_{side}")

    ankle_ctrl = "CTRL_IK_leg_" + side

    for chain in ["top", "bot"]:

        # Creation of top and bottom hierachies

        new_root_joint_name = f"JNT_{chain}_knee_flip_{side}"
        new_child_joint_name = f"JNT_{chain}_knee_flip_end_{side}"
        ik_handle = f"ikHandle_{chain}_knee_flip_{side}"

        cmds.joint(n=new_root_joint_name, rad=0.3)
        cmds.joint(n=new_child_joint_name, rad=0.3)

        root_index, child_index = 0, 2

        if chain == "bot":
            root_index, child_index = (
                2,
                0,
            )  # Switch the root joint of created chain to reverse the direction

        cmds.matchTransform(new_root_joint_name, hierarchy[root_index])
        cmds.makeIdentity(new_root_joint_name, a=1, t=0, r=1, s=0)

        cmds.matchTransform(new_child_joint_name, hierarchy[child_index])
        cmds.makeIdentity(new_child_joint_name, a=1, t=0, r=1, s=0)

        # Joints Locators Creation

        locator: str = cmds.spaceLocator(n=f"loc_{chain}_knee_flip_{side}")[0]

        cmds.matchTransform(locator, new_root_joint_name)

        if chain == "bot":
            cmds.parent(locator, ankle_ctrl)
        else:
            cmds.parent(locator, root_parent)

        # IkHandles creation

        cmds.ikHandle(
            n=ik_handle,
            sol="ikRPsolver",
            sj=new_root_joint_name,
            ee=new_child_joint_name,
            w=1,
        )

        cmds.poleVectorConstraint(locator, ik_handle, w=1)

        # Pole Vector Locator Creation

        pole_locator: str = cmds.spaceLocator(n=f"loc_{chain}_knee_{side}")[0]
        cmds.matchTransform(pole_locator, pole_vector_ctrl)

        cmds.parent(pole_locator, new_root_joint_name)

    # Parent newly created objects to their respective places

    group_top = cmds.group(n="grp_knee_" + side, em=1)
    cmds.parent(group_top, root_parent)

    cmds.parent(ik_handle, group_top)
    cmds.parent(new_root_joint_name.replace("bot", "top"), group_top)
    cmds.parent(locator.replace("bot", "top"), group_top)

    cmds.parent(ik_handle.replace("bot", "top"), ankle_ctrl)
    cmds.parent(new_root_joint_name, ankle_ctrl)

    # Constraint new locators
    cmds.pointConstraint(
        pole_locator, pole_locator.replace("bot", "top"), pole_grp, w=1
    )

    # Clean Up Scene

    set_attr(group_top, "visibility", 0)

    set_attr(ik_handle.replace("bot", "top"), "visibility", 0)
    set_attr(new_root_joint_name, "visibility", 0)
    set_attr(locator, "visibility", 0)

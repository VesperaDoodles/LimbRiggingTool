import maya.cmds as cmds

from library import *
from modules import *

def create_follicules(nurbs_plane,limb_type, patches_number):

    nurbs_name = nurbs_plane[0]

    nurbs_transform = nurbs_plane[0]

    nurbs_shape = cmds.listRelatives(nurbs_transform, shapes=True)[0]

    base_name = "bendy_" + limb_type

    side = "_" + nurbs_name[-1]

    # Group to hold follicles
    fol_group = cmds.group(empty=True, name="grp_fol_" + base_name + side)
    follicles = []

    for i in range(patches_number):

        # Create a follicle
        fol_shape = cmds.createNode(
            "follicle", n="fol_shape_" + base_name + "_" + str(i + 1) + side
        )
        fol_transform = cmds.listRelatives(fol_shape, parent=True)[0]
        cmds.rename(fol_transform, "fol_" + base_name + "_" + str(i + 1)+ side)
        fol_transform = "fol_" + base_name + "_" + str(i + 1) + side

        # Parent follicle to the group
        cmds.parent(fol_transform, fol_group)

        # Connect the follicle to the NURBS surface
        cmds.connectAttr(nurbs_shape + ".local", fol_shape + ".inputSurface")
        cmds.connectAttr(
            nurbs_transform + ".worldMatrix[0]", fol_shape + ".inputWorldMatrix"
        )
        
        # Position the follicle
        u = i / float(patches_number - 1)
        v = 0.5

        set_attr(fol_shape, "parameterU", u)
        set_attr(fol_shape, "parameterV", v)

        # Connect follicle to its transform
        cmds.connectAttr(fol_shape + ".outTranslate", fol_transform + ".translate", f=1)
        cmds.connectAttr(fol_shape + ".outRotate", fol_transform + ".rotate", f=1)

        jnt = cmds.joint(n="SK_JNT_" + base_name + "_" + str(i + 1) + side, rad = 0.2)
        cmds.matchTransform(jnt, fol_transform)
        follicles.append(fol_transform)

    return follicles, fol_group

def add_attribute(switch):

    if not cmds.attributeQuery("SineBlend",n= switch, ex=True):

        cmds.addAttr(switch, ln= "ExtraControllers", at= "bool", k=True)

        cmds.addAttr(switch, ln= "DEFORMS", at= "enum", en= "------------", k=True)

        # Sine Attributes
        cmds.addAttr(switch, ln= "SineBlend", at= "float", min=0, max=1, k=True, dv=1)
        cmds.addAttr(switch, ln= "SineAmplitude", at= "float", k=True)
        cmds.addAttr(switch, ln= "SineWaveLength", at= "float", k=True)
        cmds.addAttr(switch, ln= "SineOrientation", at= "float", k=True)
        cmds.addAttr(switch, ln= "SineOffset", at= "float", k=True)
        # Twist Attributes
        cmds.addAttr(switch, ln= "TwistBlend", at= "float", min=0, max=1, k=True, dv=1)
        cmds.addAttr(switch, ln= "TwistOffset", at= "float", k=True)
    else:
        cmds.warning("Deforms Attributes already Exists. Creation is skipped.")

def connect_attributes(blendshape, sine_handle, twist_handle):

    switch = get_loaded_text_field("txt_controller_switch")
    
    side = switch[-1]

    if radio_is_checked("rad_limb_biped_arm"):
        limb_type = BipedLimb.Arm
    else :
        limb_type = BipedLimb.Leg

    side = switch[-1]

    sine_node = cmds.listRelatives(sine_handle)[0]
    twist_node = cmds.listRelatives(twist_handle)[0]

    # Connect blendshapes weights 
    connect_attr(switch, "SineBlend", blendshape, f"nurbs_{limb_type}_sine_{side}")
    connect_attr(switch, "TwistBlend", blendshape, f"nurbs_{limb_type}_twist_{side}")

    # Connect Sine 

    connect_attr(switch, "SineAmplitude", sine_node, "amplitude")
    connect_attr(switch, "SineWaveLength", sine_node, "wavelength")
    connect_attr(switch, "SineOffset", sine_node, "offset")

    connect_attr(switch, "SineOrientation", sine_handle[1], "rotateY")

    # Connect Twist

    offset_attr = "startAngle"

    if side == "L" and limb_type == BipedLimb.Arm:
        offset_attr = "endAngle"

    connect_attr(switch, "TwistOffset", twist_node, offset_attr)

def create_blendshape(nurbs_limb, nurbs_sine, nurbs_twist):

    switch = get_loaded_text_field("txt_controller_switch")
    
    side = switch[-1]

    if radio_is_checked("rad_limb_biped_arm"):
        limb_type = BipedLimb.Arm
    else :
        limb_type = BipedLimb.Leg
    
    base_name = f"{limb_type}_bendy"

    cmds.select(nurbs_sine)
    cmds.select(nurbs_twist, add=True)
    cmds.select(nurbs_limb, add=True)

    blendshape_node = cmds.blendShape(n=f"bs_{limb_type}_bendy_{nurbs_limb[-1]}")

    cmds.select(nurbs_sine)
    sine = cmds.nonLinear(n= f"sine_{limb_type}_bendy_{side}", typ= "sine")
    cmds.rotate(90, z=True, os=True, r=True, fo=True)
    
    cmds.select(nurbs_twist)
    twist = cmds.nonLinear(n= f"twist_{limb_type}_bendy_{side}", typ= "twist")
    cmds.rotate(90, z=True, os=True, r=True, fo=True)

    cmds.parent( sine, f"grp_deforms_{base_name}_{side}")
    cmds.parent( twist, f"grp_deforms_{base_name}_{side}")

    add_attribute(switch)
    connect_attributes(blendshape_node[0], sine, twist)

def create_bendy_limb(*args):

    ##############
    # User Inputs
    root = get_loaded_text_field("txt_joint_root")
    switch = get_loaded_text_field("txt_controller_switch")

    side = switch[-1]

    hierarchy = get_hierachy(root)

    if radio_is_checked("rad_limb_biped_arm"):
        limb_type = BipedLimb.Arm
    else :
        limb_type = BipedLimb.Leg

    # Creates a Ribbon on the limb

    u_count = 8
    base_name = f"{limb_type}_bendy"
    
    root_joint = hierarchy[0]
    middle_joint = hierarchy[1]
    end_joint = hierarchy[2]

    # Create the main ribbon and deformers ribbons
    nurbs_limb = cmds.nurbsPlane(n=f"nurbs_{limb_type}_{side}", u=u_count, lr = 0.16, w=u_count*5, ax= [0,0,1])
    nurbs_transform = nurbs_limb[0]

   # Make Ribbon vertical if the limb is a leg

    if limb_type == BipedLimb.Leg:

        cmds.select(nurbs_limb)
        cmds.rotate(90, z=True,os=True, r=True, fo=True)
    
    # Get the middle joint position
    middle_position = cmds.xform(middle_joint,ws=True,t=True, q=True)

     # Move the main ribbon to the middle joint and freeze tranforms
    cmds.xform(nurbs_limb, t=[middle_position[0], middle_position[1], 0])

    cmds.makeIdentity(nurbs_limb, t=True, a=True)

    cmds.insertKnotSurface(nurbs_transform, ch=True, nk=1, add=True, ib=0, rpo=True, p = 0.48)
    cmds.insertKnotSurface(nurbs_transform, ch=True, nk=1, add=True, ib=0, rpo=True, p = 0.52)
    
    follicles, fol_group = create_follicules(nurbs_limb, limb_type, u_count+1)

    cmds.delete(nurbs_transform, ch=True)
    nurbs_limb = nurbs_transform

    # Determine which main joints to duplicate and constrain
    selected_indices = [
        int(round(i * ((u_count) / float(4))))
        for i in range(5)
    ]

    arm_is_reversed = False

    root_joint_position = cmds.xform(cmds.listRelatives(follicles[0])[1], q=True, ws=True, t=True)
    end_joint_position = cmds.xform(cmds.listRelatives(follicles[-1])[1], q=True, ws=True, t=True)
    if limb_type == BipedLimb.Arm:

        if root_joint_position[0] < end_joint_position[0]:
            # If the X position of the root joint (under the root follicle) is bigger than the end joint; then the list needs to be reversed
            #selected_indices.reverse()
            arm_is_reversed = True

        controls_normal_axis = (1,0,0)

    else: # Leg
        if root_joint_position[1] < end_joint_position[1]:
            # If the Y position of the root joint (under the root follicle) is bigger than the end joint; then the list needs to be reversed
            selected_indices.reverse()
        controls_normal_axis = (0,1,0)

    bind_joints = []

    LIMB_PARTS = [ "root", "upper", "middle", "lower", "end"]
    for limb_part, selected_index in zip(LIMB_PARTS, selected_indices): # Loop to rename joints

        target_joint = cmds.listRelatives(follicles[selected_index])[1]
        created_joint = ""

        created_joint = cmds.duplicate(target_joint, n= f"JNT_{limb_part}_{base_name}_{side}")[0]

        if limb_part not in ["upper", "lower"] and limb_type == BipedLimb.Arm and side == "L":
            #set_attr(created_joint, "jointOrientY", 180)
            print("hello")

        cmds.parent(created_joint, w=True)

        set_attr(created_joint, "radius", 4)
        bind_joints.append(created_joint)

    if arm_is_reversed:
        print(bind_joints)
        #bind_joints.reverse()
        print("Reversed :", bind_joints)
    
    nurbs_sine = cmds.duplicate(nurbs_transform, n=f"nurbs_{limb_type}_sine_{side}")
    nurbs_twist = cmds.duplicate(nurbs_transform, n=f"nurbs_{limb_type}_twist_{side}")

    unlock_transforms(nurbs_sine[0])
    unlock_transforms(nurbs_twist[0])

    world_space = cmds.group(em=True)

    cmds.matchTransform(nurbs_sine, world_space)
    cmds.matchTransform(nurbs_twist, world_space)

    cmds.delete(world_space)

    misc_group = cmds.group(em=True, n=f"grp_misc_{base_name}_{side}")
    deforms_group = cmds.group(em=True, n=f"grp_deforms_{base_name}_{side}")

    cmds.parent(deforms_group, misc_group )

    cmds.parent(nurbs_sine, deforms_group )
    cmds.parent(nurbs_twist, deforms_group )
    cmds.parent(fol_group, misc_group)


    set_attr(misc_group, "visibility", 0)
    set_attr(deforms_group, "visibility", 0)

    create_blendshape(nurbs_limb, nurbs_sine, nurbs_twist)

    cmds.select(cl=True)
    for joint in bind_joints:
        cmds.select(joint, add=True)

    cmds.select(nurbs_transform, add=True)
    cmds.skinCluster()

    controls_group = cmds.group(em=True, n= f"GRP_{base_name}_{side}")

    for i, joint in enumerate(bind_joints):

        print(joint)

        target = joint

        # Create Controller for middle joints
        if i != 0 and i!= 4:

            controller = cmds.circle(n=joint.replace("JNT", "CTRL"), r=4,nr= controls_normal_axis )[0]
            
            cmds.matchTransform(controller, joint, pos=True, rot=False)
            target = controller

            if i != 2:

                aim_offset = cmds.group(controller, n= joint.replace("JNT", "aim_offset"))
                target = aim_offset
        
            else: 
                aim_point_middle = cmds.group(controller, n= joint.replace("JNT", "aim_point"))
                target = aim_point_middle

        elif i == 0 :

            aim_point_root = cmds.group(joint, n= joint.replace("JNT", "aim_point"))
            target = aim_point_root

        # Create Offsets Group

        offset_group = cmds.group(target, n= joint.replace("JNT", "offset"))

        if i != 0 and i!= 4:
            cmds.makeIdentity(controller, t=True, r=True, a=True)
            cmds.parent(joint, controller)

        # Add Constaints

        if limb_type == BipedLimb.Leg:

            aim_vector = (0, -1, 0)
        else:
            if side == "L":
                aim_vector = (1, 0, 0) # tkt
            else:
                aim_vector = (-1, 0, 0)

        if i%2 == 0:

            constraint(hierarchy[i//2], offset_group, translate_value=True, orient_value=False, scale_value=False, maintain_offset_value=False)
            constraint(hierarchy[i//2], offset_group, translate_value=False, orient_value=True, scale_value=False, maintain_offset_value=True)

        elif i == 1:
            cmds.pointConstraint(bind_joints[0], bind_joints[2], offset_group, mo=False)

            cmds.aimConstraint(bind_joints[2], joint.replace("JNT", "aim_offset"), wuo = aim_point_root, aim= aim_vector)

        else : 
            cmds.pointConstraint(bind_joints[2], bind_joints[4], offset_group, mo=False)

            cmds.aimConstraint(bind_joints[4], joint.replace("JNT", "aim_offset"), wuo = aim_point_middle, aim= aim_vector)
        
        set_attr(joint, "visibility", 0)
        cmds.parent(offset_group, controls_group, r=True)

    # Clean Up

    cmds.parent(nurbs_limb, misc_group)
    connect_attr(switch, "ExtraControllers", controls_group, "visibility")
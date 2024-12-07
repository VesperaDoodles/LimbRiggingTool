import maya.cmds as cmds
import functools
from typing import *
from lib import *

myLimbObject = None
myHandObject = None

def getLimbObject():
  global myLimbObject
  if myLimbObject is None:
    myLimbObject = LimbClass()
  return myLimbObject

def getHandObject():
  global myHandObject
  if myHandObject is None:
    myHandObject = HandClass()
  return myHandObject

class LimbClass:
    root_joint: str
    switch: str
    switch_attribute:str

    side:str

    limb_joint_number: int
    limb_type:str

    hierarchy: List[str]
    joints_prefix: List[str]

    ik_control:str
    pole_control:str

    def __init__(self):

        self.root_joint =  get_loaded_text_field("txt_joint_root")

        root_parents = cmds.listRelatives(self.root_joint, p=True)
        self.root_parent = root_parents[0]

        self.switch = get_loaded_text_field("txt_controller_switch")
        self.switch_attribute = ".switchFKIK"

        self.limb_joint_number = 3 if radio_is_checked("rad_limb_biped") else 4
        self.limb_type = "biped" if radio_is_checked("rad_limb_biped") else "quadruped"

        

        if self.limb_type == "biped":
            if  radio_is_checked("rad_limb_biped_arm"):
                self.limb_name = "arm" 
            else : 
                self.limb_name ="leg"
                self.limb_joint_number = 5

        else:
            self.limb_name = "front" if radio_is_checked("rad_limb_quadruped_front") else "rear"
        
        self.side = self.root_joint[-1]

        self.suffix_name = self.limb_name + "_" + self.side

        self.hierarchy = get_hierachy(self.root_joint)
        self.joints_prefix = ["FK_", "IK_"]

        if is_checked("ckb_limb_stretch"):
            self.joints_prefix.append("stretch_")

        # ---------------------------
        # Controlers 

        self.root_fk_control = self.root_joint.replace("SK_JNT", "CTRL_FK")

        self.ik_control = "CTRL_IK_" + self.suffix_name

        self.pole_control = "CTRL_pole_" + self.suffix_name

    def show_attributes(self):

        print("Root Joint:", self.root_joint)
        print("Switch Control:", self.switch)
        print("Limb Type:", self.limb_type)

        print("Hierarchy:", self.hierarchy)

    def duplicate_hierarchy(self):

        self.show_attributes()
            
        # For each joint, we duplicate it, clean all rotations, rename it and put it in the correct hierachy
        # (IK, FK)
        
        self.joints_prefix: List[str] = ["FK_", "IK_"]

        cmds.select(cl=True)

        for new_joint_prefix in self.joints_prefix:

            for i in range(self.limb_joint_number):
                
                new_joint_name = self.hierarchy[i]
                print(new_joint_prefix, new_joint_name)

                new_joint_name = new_joint_name.replace("SK_", new_joint_prefix)

                cmds.joint(n=new_joint_name, rad = 0.3)

                cmds.matchTransform(new_joint_name, self.hierarchy[i])

                cmds.makeIdentity(new_joint_name, a=1, t=0, r=1, s=0)
                
            cmds.select(cl=True)

        ik_root = self.root_joint.replace("SK_", "IK_")
        fk_root = self.root_joint.replace("SK_", "FK_")

        cmds.parent(ik_root, self.root_parent)
        cmds.parent(fk_root, self.root_parent)
    
    def pair_blend(self):
    
        blend_jointsList: List[str] = ["IK_", "FK_"]

        # We only process the first n elements, where n is `limb_joints`.

        for sk_jnt in self.hierarchy[:self.limb_joint_number]:

            jnt = sk_jnt.replace("SK_", "")
            ik_jnt = blend_jointsList[0] + jnt
            fk_jnt = blend_jointsList[1] + jnt

            # IK will be 1 and FK will be 2
            cmds.shadingNode("pairBlend", au=1, n="pairBlend_" + jnt)

            cmds.connectAttr(
                (ik_jnt + ".translate"), ("pairBlend_" + jnt + ".inTranslate1"), f=1
            )
            cmds.connectAttr((ik_jnt + ".rotate"), ("pairBlend_" + jnt + ".inRotate1"), f=1)

            cmds.connectAttr(
                (fk_jnt + ".translate"), ("pairBlend_" + jnt + ".inTranslate2"), f=1
            )
            cmds.connectAttr((fk_jnt + ".rotate"), ("pairBlend_" + jnt + ".inRotate2"), f=1)

            cmds.connectAttr(
                ("pairBlend_" + jnt + ".outTranslate"), (sk_jnt + ".translate"), f=1
            )
            cmds.connectAttr(("pairBlend_" + jnt + ".outRotate"), (sk_jnt + ".rotate"), f=1)

            cmds.connectAttr(
                (self.switch + self.switch_attribute), ("pairBlend_" + jnt + ".weight"), f=1
            )

    def add_stretch(self):
        print()
        
    def biped_rig(self):


        rig_group = "grp_" + self.suffix_name
        cmds.group(n=rig_group, em=True, w=True)

        # ------------------------------------------------------------------------
        # Setup FK

        # Connect FK controls to new joints
        for i in range(self.limb_joint_number):

            # Creation of FK controllers
            tempJoint = self.hierarchy[i].replace("SK_JNT", "")
            create_control_fk(self.hierarchy[i], self.side, 1)
            tempctrl = parent_control_fk(self.hierarchy, i)
            if i == 0:
                cmds.parent(tempctrl, rig_group)
            constraint(
                ("CTRL_FK" + tempJoint),
                (self.hierarchy[i].replace("SK", "FK")),
                translate_value=False,
                maintain_offset_value=0)  # orient constraint
            
        # ------------------------------------------------------------------------
        # Setup IK

        create_control_ik(
            self.hierarchy, self.hierarchy[2], self.side, self.ik_control, self.pole_control
        )

        cmds.parent(self.ik_control.replace("CTRL", "offset"), rig_group)
        cmds.parent(self.pole_control.replace("CTRL", "offset"),  rig_group)

        # Create the main IK Handle from root to end joint (hip/shoulder > ankle wrist)
        cmds.ikHandle(
            n=("IKHandle_" + self.suffix_name),
            sol="ikRPsolver",
            sj=(self.hierarchy[0].replace("SK", "IK")),
            ee=((self.hierarchy[2].replace("SK", "IK"))),
        )
        set_attr("IKHandle_" + self.suffix_name, "visibility", 0)

        # Parent the IK handle to the group to the end control
        cmds.parent(("IKHandle_" + self.suffix_name), self.ik_control)

        cmds.poleVectorConstraint(self.pole_control, ("IKHandle_" + self.suffix_name), w=1)
        constraint(
            self.ik_control,
            self.hierarchy[2].replace("SK", "IK"),
            translate_value=False,
            orient_value=True, maintain_offset_value=1
        )

        offsetZ = cmds.getAttr(self.pole_control.replace("CTRL", "offset") + ".translateZ")
        cmds.select(self.pole_control.replace("CTRL", "offset"))

        if offsetZ <= 0:
            cmds.move(-15, z=True)
        else:
            cmds.move(15, z=True)

        # Final Touch Ups in viewport -> Hide the FK controllers in IK mode and the IK controllers in FK mode

        cmds.connectAttr(
            (self.switch + ".switchFKIK"), (self.root_fk_control + ".visibility"), f=1
        )
        cmds.shadingNode("reverse", n=(self.suffix_name + "_fkik_reverse"), au=1)

        cmds.connectAttr(
            (self.switch + ".switchFKIK"), (self.suffix_name + "_fkik_reverse.inputX"), f=1
        )
        cmds.connectAttr(
            (self.suffix_name + "_fkik_reverse.outputX"), (self.ik_control + ".visibility"), f=1
        )
        cmds.connectAttr(
            (self.suffix_name + "_fkik_reverse.outputX"), (self.pole_control + ".visibility"), f=1)
        
        if is_checked("ckb_limb_stretch"):
            stretch(self.root_joint, self.hierarchy, self.suffix_name, self.ik_control, self.switch)

        # Adds the unbreakable knee setup

        if self.limb_name == "leg":
            add_unbreakable_knees(self.pole_control, self.hierarchy, self.root_parent)


class HandClass:

    def __init__(self):

        shoulder = get_loaded_text_field("txt_joint_root")
        self.side =  shoulder[-1]

        self.wrist_joint =  "SK_JNT_wrist_" + self.side
        

        self.switch = get_loaded_text_field("txt_controller_switch")

        self.hierarchy = get_hierachy(self.wrist_joint)


    def add_custom_attributes(self):

        cmds.addAttr(self.switch, ln="FingersOptions", at="enum", en= "------------",k=True )

    
    def add_fingers_controls(self):

        fingers_list = ["index", "middle", "ring", "pinkie"]

        root_phalanges = cmds.group("grp_hand_"+ self.side,em=1)

        for finger in fingers_list:

            for i in range(1,4):

                phalange = f"SK_JNT_{finger}_0{i}_{self.side}"
                print(phalange)

                ctrl = phalange.replace("SK_JNT", "CTRL_FK")
                create_control_fk(phalange, self.side, 2)

                # Creates group for customs attibutes
                
                grp1 = cmds.group(ctrl,name=phalange.replace("SK_JNT", "GRP1"))
                grp2 = cmds.group(grp1,name=phalange.replace("SK_JNT", "GRP2"))

                # Creation of Constraints

                if ("1" in phalange) :
                    cmds.parent(f"offset_FK_{finger}_0{i}_{self.side}", root_phalanges)
                    cmds.parentConstraint(ctrl, phalange, w=1, mo=1)
                else:
                    cmds.orientConstraint(ctrl, phalange, w=1, mo=1 )
                    cmds.parent(f"offset_FK_{finger}_0{i}_{self.side}", previous_ctrl)

                previous_ctrl = ctrl

        finger = "thumb"
        for i in range(0,3):
                
            if i == 0:
                    phalange = f"SK_JNT_meta_{finger}_{self.side}"
            else:
                phalange = f"SK_JNT_{finger}_0{i}_{self.side}"
                
            print(phalange)

            ctrl = phalange.replace("SK_JNT", "CTRL_FK")

            create_control_fk(phalange, self.side, 2)

            # Creates group for customs attibutes
            
            grp1 = cmds.group(ctrl,name=phalange.replace("SK_JNT", "GRP1"))
            grp2 = cmds.group(grp1,name=phalange.replace("SK_JNT", "GRP2"))

            # Creation of Constraints

            if i == 0 :
                cmds.parentConstraint(ctrl, phalange, w=1, mo=1)
                cmds.parent(f"offset_FK_meta_{finger}_{self.side}", root_phalanges)
            else:
                cmds.orientConstraint(ctrl, phalange, w=1, mo=1 )
                cmds.parent(f"offset_FK_{finger}_0{i}_{self.side}", previous_ctrl)

            previous_ctrl = ctrl
        self.add_custom_attributes()

def duplicate_hierarchies_callback(*args):
    getLimbObject().duplicate_hierarchy()

def pair_blend_callback(*args):
    getLimbObject().pair_blend()

def add_controls_callback(*args):

    if getLimbObject().limb_type == "biped":
        getLimbObject().biped_rig()
    else:
        getLimbObject().biped_rig()

def add_hand_controls_callback(*args):
    getHandObject().add_fingers_controls()
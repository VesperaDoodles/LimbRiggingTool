import maya.cmds as cmds

from typing import *
from library import *
from modules import *

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
    switch_attribute: str

    scale:float

    side: str

    limb_joint_number: int
    limb_type: str

    hierarchy: List[str]
    JOINTS_PREFIX: List[str]

    ik_control: str
    pole_control: str

    def __init__(self):

        self.root_joint = get_loaded_text_field("txt_joint_root")
        self.scale = get_float_field("ff_limb_scale")

        if len(self.root_joint) == 0:
            raise ValueError ("Please load a root joint.")

        self.limb_type = "biped" if radio_is_checked("rad_limb_biped") else "quadruped"

        self.hierarchy = get_hierachy(self.root_joint)

        self.limb_joint_number = 3 if radio_is_checked("rad_limb_biped") else 4

        if self.limb_type == "biped":
            if radio_is_checked("rad_limb_biped_arm"):
                self.limb_name = BipedLimb.Arm
            else:

                if len(self.hierarchy) >= 5 :  # Check if a foot is included
                    self.limb_joint_number = 5

                self.limb_name = BipedLimb.Leg

        else:
            self.limb_name = (
                "front" if radio_is_checked("rad_limb_quadruped_front") else "rear"
            )

        self.side = self.root_joint[-1]

        self.suffix_name = self.limb_name + "_" + self.side

        root_parents: List[str] = cmds.listRelatives(self.root_joint, p=True)

        if root_parents == None:
            group = cmds.group(n="grp_rig_" + self.suffix_name, em=True)
            cmds.parent(self.root_joint, group)
            root_parents = [group]

        self.root_parent = root_parents[0]

        self.switch = get_loaded_text_field("txt_controller_switch")

        if len(self.switch) == 0:
            raise ValueError("Please load a switch controller.")

        self.switch_attribute = ".switchFKIK"

        if not cmds.attributeQuery("switchFKIK", ex=True, n=self.switch):

            cmds.warning("No Switch Attribute found, creating one")
            cmds.addAttr(self.switch, ln="switchFKIK", at="float", min=0, max=1, k=True)

        self.JOINTS_PREFIX = [NameConvention.fk + "_", NameConvention.ik + "_"]

        # ---------------------------
        # Controlers

        self.root_fk_control = self.root_joint.replace(NameConvention.main, f"{NameConvention.controller}_{NameConvention.fk}")

        self.ik_control = f"{NameConvention.controller}_{NameConvention.ik}_" + self.suffix_name

        self.pole_control = f"{NameConvention.controller}_pole_" + self.suffix_name

    def duplicate_hierarchy(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Duplicates the SK hierarchies, clears rotations, renames and parents to the root parent 

        ###################################

        cmds.select(cl=True)

        for new_joint_prefix in self.JOINTS_PREFIX:

            for i in range(self.limb_joint_number):

                new_joint_name = self.hierarchy[i]

                new_joint_name = new_joint_name.replace(NameConvention.main + "_", new_joint_prefix)

                cmds.joint(n=new_joint_name, rad=0.3)

                cmds.matchTransform(new_joint_name, self.hierarchy[i])

                cmds.makeIdentity(new_joint_name, a=1, t=0, r=1, s=0)

            cmds.select(cl=True)

        ik_root = self.root_joint.replace(NameConvention.main, NameConvention.ik)
        fk_root = self.root_joint.replace(NameConvention.main, NameConvention.fk)

        cmds.parent(ik_root, self.root_parent)
        cmds.parent(fk_root, self.root_parent)

    def pair_blend(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Blends FK and IK Hierarchies and connect to SK hierarchies

        ###################################

        blend_jointsList: List[str] = [NameConvention.ik, NameConvention.fk]

        # We only process the first n elements, where n is `limb_joints`.

        for sk_jnt in self.hierarchy[: self.limb_joint_number]:

            jnt = sk_jnt.replace(NameConvention.main, "")
            ik_jnt = blend_jointsList[0] + jnt
            fk_jnt = blend_jointsList[1] + jnt

            # IK will be 1 and FK will be 2
            cmds.shadingNode("pairBlend", au=1, n="pairBlend_" + jnt)

            cmds.connectAttr(
                (ik_jnt + ".translate"), ("pairBlend_" + jnt + ".inTranslate1"), f=1
            )
            cmds.connectAttr(
                (ik_jnt + ".rotate"), ("pairBlend_" + jnt + ".inRotate1"), f=1
            )

            cmds.connectAttr(
                (fk_jnt + ".translate"), ("pairBlend_" + jnt + ".inTranslate2"), f=1
            )
            cmds.connectAttr(
                (fk_jnt + ".rotate"), ("pairBlend_" + jnt + ".inRotate2"), f=1
            )

            cmds.connectAttr(
                ("pairBlend_" + jnt + ".outTranslate"), (sk_jnt + ".translate"), f=1
            )
            cmds.connectAttr(
                ("pairBlend_" + jnt + ".outRotate"), (sk_jnt + ".rotate"), f=1
            )

            cmds.connectAttr(
                (self.switch + self.switch_attribute),
                ("pairBlend_" + jnt + ".weight"),
                f=1,
            )

        self.lock_switch_transform()

    def lock_switch_transform(self):

        lock_transforms(self.switch, to_lock=True)
        cmds.setAttr(self.switch + ".visibility", lock=True )
        cmds.setAttr(self.switch + ".visibility", keyable=False )

    def biped_rig(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Rigs a biped limb with FK /IK blending, stretch system if specified, unbreakable knee pivot if specified 

        ###################################

        rig_group = "grp_" + self.suffix_name
        cmds.group(n=rig_group, em=True, w=True)

    
        # ------------------------------------------------------------------------
        # Setup FK

        # Connect FK controls to new joints

        for i in range(self.limb_joint_number):

            # Creation of FK controllers
            tempJoint = self.hierarchy[i].replace(NameConvention.main, "")
            create_control_fk(self.hierarchy[i], self.side, self.scale)
            tempctrl = parent_control_fk(self.hierarchy, i)
            if i == 0:
                cmds.parent(tempctrl, rig_group)
            constraint(
                (f"{NameConvention.controller}_{NameConvention.fk}" + tempJoint),
                (self.hierarchy[i].replace(NameConvention.main, NameConvention.fk)),
                translate_value=False,
                maintain_offset_value=0,
            )  # orient constraint

        # ------------------------------------------------------------------------
        # Setup IK

        create_control_ik(
            self.hierarchy,
            self.hierarchy[2],
            self.side,
            self.ik_control,
            self.pole_control,
        )

        cmds.parent(self.ik_control.replace(NameConvention.controller, "offset"), rig_group)
        cmds.parent(self.pole_control.replace(NameConvention.controller, "offset"), rig_group)

        # Create the main IK Handle from root to end joint (hip/shoulder > ankle wrist)
        cmds.ikHandle(
            n=("IkHandle_" + self.suffix_name),
            sol="ikRPsolver",
            sj=(self.hierarchy[0].replace(NameConvention.main, NameConvention.ik)),
            ee=((self.hierarchy[2].replace(NameConvention.main, NameConvention.ik))),
        )
        set_attr("IkHandle_" + self.suffix_name, "visibility", 0)

        # Parent the IK handle to the group to the end control
        cmds.parent(("IkHandle_" + self.suffix_name), self.ik_control)

        cmds.poleVectorConstraint(
            self.pole_control, ("IkHandle_" + self.suffix_name), w=1
        )

        constraint(
            self.ik_control,
            self.hierarchy[2].replace(NameConvention.main, NameConvention.ik),
            translate_value=False,
            orient_value=True,
            maintain_offset_value=0,
        )

        # Final Touch Ups in viewport -> Hide the FK controllers in IK mode and the IK controllers in FK mode

        cmds.connectAttr(
            (self.switch + ".switchFKIK"), (self.root_fk_control + ".visibility"), f=1
        )
        cmds.shadingNode("reverse", n=(self.suffix_name + "_fkik_reverse"), au=1)

        cmds.connectAttr(
            (self.switch + ".switchFKIK"),
            (self.suffix_name + "_fkik_reverse.inputX"),
            f=1,
        )
        cmds.connectAttr(
            (self.suffix_name + "_fkik_reverse.outputX"),
            (self.ik_control + ".visibility"),
            f=1,
        )
        cmds.connectAttr(
            (self.suffix_name + "_fkik_reverse.outputX"),
            (self.pole_control + ".visibility"),
            f=1,
        )

        if is_checked("ckb_limb_stretch"):
            is_biped = True if self.limb_type == "biped" else False
            stretch(
                self.root_joint,
                self.hierarchy,
                self.suffix_name,
                self.ik_control,
                self.switch,
                is_biped,
            )

        # Adds the unbreakable knee setup

        cmds.select(cl=1)

        if is_checked("ckb_better_pole"):
            add_unbreakable_knees(self.pole_control, self.hierarchy, self.root_parent)

    def foot_roll(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Adds an IK foot roll system 

        ###################################

        heel_joint = get_loaded_text_field("txt_foot_root")

        foot_hierarchy = get_hierachy(heel_joint)

        if len(foot_hierarchy) < 4:
            raise IndexError ("The reverse foot hierarchy must contain 4 joints : heel, toe, ball and ankle.")

        cmds.ikHandle(
            n=("IkHandle_ball_" + self.side),
            sol="ikSCsolver",
            sj=(self.hierarchy[2].replace(NameConvention.main, NameConvention.ik)),
            ee=((self.hierarchy[3].replace(NameConvention.main, NameConvention.ik))),
        )
        set_attr("IkHandle_ball_" + self.side, "visibility", 0)

        cmds.ikHandle(
            n=("IkHandle_toe_" + self.side),
            sol="ikSCsolver",
            sj=(self.hierarchy[3].replace(NameConvention.main, NameConvention.ik)),
            ee=((self.hierarchy[4].replace(NameConvention.main, NameConvention.ik))),
        )
        set_attr("IkHandle_toe_" + self.side, "visibility", 0)

        cmds.parent("IkHandle_ball_" + self.side, foot_hierarchy[2])
        cmds.parent("IkHandle_toe_" + self.side, foot_hierarchy[1])

        cmds.parent("IkHandle_" + self.suffix_name, foot_hierarchy[-1])

        cmds.parent(heel_joint, self.ik_control)


class HandClass:

    def __init__(self):

        shoulder = get_loaded_text_field("txt_joint_root")
        self.side = shoulder[-1]

        self.wrist_joint = NameConvention.main+ "_wrist_" + self.side

        self.switch = get_loaded_text_field("txt_controller_switch")

        self.hierarchy = get_hierachy(self.wrist_joint)

    def add_custom_attributes(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Adds Attributes to Switch Controller

        ###################################

        fingers_list = ["index", "middle", "ring", "pinkie"]

        if not cmds.attributeQuery("FingersOptions", ex=True, n=self.switch):
            cmds.addAttr(
                self.switch, ln="FINGERS", at="enum", en="------------", k=True
            )

        spread_attr = f"Spread"
        orient_attr = "Orient"

        cmds.addAttr(
            self.switch, ln=spread_attr, at="float", min=-5, max=5, dv=0, k=True
        )
        cmds.addAttr(
            self.switch, ln=orient_attr, at="float", min=-5, max=5, dv=0, k=True
        )

        cmds.addAttr(
            self.switch, ln=f"CurlThumb", at="float", min=-10, max=5, dv=0, k=True
        )

        for finger in fingers_list:

            curl_attr = f"Curl{finger.capitalize()}"

            cmds.addAttr(
                self.switch, ln=curl_attr, at="float", min=-10, max=5, dv=0, k=True
            )

            float_math_node = cmds.shadingNode(
                "floatMath", n=f"floatMath_{finger}_curl", au=True
            )

            set_attr(float_math_node, "operation", 2)

            float_math_node_spread = cmds.shadingNode(
                "floatMath", n=f"floatMath_{finger}_spread", au=True
            )
            float_math_node_orient = cmds.shadingNode(
                "floatMath", n=f"floatMath_{finger}_orient", au=True
            )

            set_attr(float_math_node_spread, "operation", 2)
            set_attr(float_math_node_orient, "operation", 2)

            if finger == "index":
                mult_value = 2
            elif finger == "middle":
                mult_value = 0
            elif finger == "ring":
                mult_value = -2
            else:
                mult_value = -4

            set_attr(float_math_node_spread, "floatB", mult_value)
            set_attr(float_math_node_orient, "floatB", mult_value)

            for i in range(1, 4):

                grp_curl_spread = f"GRP1_{finger}_0{i}_{self.side}"
                grp_orient = f"GRP2_{finger}_0{i}_{self.side}"

                connect_attr(self.switch, curl_attr, float_math_node, "floatA")
                connect_attr(float_math_node, "outFloat", grp_curl_spread, "rotateZ")

                if i == 1:

                    connect_attr(
                        self.switch, spread_attr, float_math_node_spread, "floatA"
                    )
                    connect_attr(
                        float_math_node_spread, "outFloat", grp_curl_spread, "rotateY"
                    )

                    connect_attr(
                        self.switch, orient_attr, float_math_node_orient, "floatA"
                    )
                    connect_attr(
                        float_math_node_orient, "outFloat", grp_orient, "rotateZ"
                    )

        # Thumb Attribute

        finger = "thumb"

        curl_attr = f"Curl{finger.capitalize()}"

        float_math_node = cmds.shadingNode(
            "floatMath", n=f"floatMath_{finger}_curl", au=True
        )
        set_attr(float_math_node, "operation", 2)

        for i in range(0, 3):

            if i == 0:
                grp_curl_spread = f"GRP1_meta_{finger}_{self.side}"
            else:
                grp_curl_spread = f"GRP1_{finger}_0{i}_{self.side}"

            connect_attr(self.switch, curl_attr, float_math_node, "floatA")
            connect_attr(float_math_node, "outFloat", grp_curl_spread, "rotateY")

    def update_values(self, changed_attr):

        ###################################

        # Inputs - self, str ; changed_attr, str
        # Returns - None

        # Updates the newly changed attribute on all fingers connections

        ###################################

        for finger in ["index", "middle", "ring", "pinkie"]:

            if changed_attr == "curl":
                attr = f"floatMath_{finger}_curl"
                mult = get_slider_field("sld_curl")

            elif changed_attr == "spread":
                attr = f"floatMath_{finger}_spread"
                mult = get_slider_field("sld_spread")
            else:
                attr = f"floatMath_{finger}_orient"
                mult = get_slider_field("sld_orient")

            if finger == "index":
                mult_value = 2
            elif finger == "middle":
                mult_value = 0
            elif finger == "ring":
                mult_value = -2
            else:
                mult_value = -4

            if changed_attr == "curl":

                mult_value = 1
                # Thumb Curl
                set_attr(f"floatMath_thumb_curl", "floatB", mult * 0.5)

            set_attr(attr, "floatB", mult * mult_value)

    def add_fingers_controls(self):

        ###################################

        # Inputs - self, str
        # Returns - None

        # Adds FK Controllers to all phalanges

        ###################################

        fingers_list = ["index", "middle", "ring", "pinkie"]

        root_phalanges = cmds.group(n="grp_rig_hand_" + self.side, em=1)

        # Parent Hand Group
        cmds.matchTransform(root_phalanges, self.wrist_joint, pos=True)
        cmds.parentConstraint(
            self.wrist_joint,
            root_phalanges,
            w=1,
        )

        for finger in fingers_list:

            for i in range(1, 4):

                phalange = f"{NameConvention.main}_{finger}_0{i}_{self.side}"

                ctrl = phalange.replace(NameConvention.main, NameConvention.controller + "_" + NameConvention.fk)
                create_control_fk(phalange, self.side, 2)

                # Creates group for customs attibutes

                grp1 = cmds.group(ctrl, name=phalange.replace(NameConvention.main, "GRP1"))
                grp2 = cmds.group(grp1, name=phalange.replace(NameConvention.main, "GRP2"))

                # Creation of Constraints

                if "1" in phalange:
                    cmds.parent(f"offset_{NameConvention.fk}_{finger}_0{i}_{self.side}", root_phalanges)
                    cmds.parentConstraint(ctrl, phalange, w=1, mo=1)
                else:
                    cmds.orientConstraint(ctrl, phalange, w=1, mo=1)
                    cmds.parent(f"offset_{NameConvention.fk}_{finger}_0{i}_{self.side}", previous_ctrl)

                previous_ctrl = ctrl

        finger = "thumb"

        for i in range(0, 3):

            if i == 0:
                phalange = f"{NameConvention.main}_meta_{finger}_{self.side}"
            else:
                phalange = f"{NameConvention.main}_{finger}_0{i}_{self.side}"

            ctrl = phalange.replace(NameConvention.main, f"{NameConvention.controller}_{NameConvention.fk}")

            create_control_fk(phalange, self.side, 2)

            # Creates group for customs attibutes
            grp1 = cmds.group(ctrl, name=phalange.replace(NameConvention.main, "GRP1"))
            grp2 = cmds.group(grp1, name=phalange.replace(NameConvention.main, "GRP2"))

            # Creation of Constraints
            if i == 0:
                cmds.parentConstraint(ctrl, phalange, w=1, mo=1)
                cmds.parent(f"offset_{NameConvention.fk}_meta_{finger}_{self.side}", root_phalanges)
            else:
                cmds.orientConstraint(ctrl, phalange, w=1, mo=1)
                cmds.parent(f"offset_{NameConvention.fk}_{finger}_0{i}_{self.side}", previous_ctrl)

            previous_ctrl = ctrl

        self.add_custom_attributes()


def duplicate_hierarchies_callback(*args):
    getLimbObject().duplicate_hierarchy()
    getLimbObject().pair_blend()


def add_controls_callback(*args):

    if getLimbObject().limb_type == "biped":
        getLimbObject().biped_rig()
    else:
        getLimbObject().biped_rig()


def add_hand_controls_callback(*args):
    getHandObject().add_fingers_controls()


def add_foot_roll_callback(*args):
    getLimbObject().foot_roll()


def update_curl_attributes_callback(*args):
    getHandObject().update_values("curl")


def update_spread_attributes_callback(*args):
    getHandObject().update_values("spread")


def update_orient_attributes_callback(*args):
    getHandObject().update_values("orient")

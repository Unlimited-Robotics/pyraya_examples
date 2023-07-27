import numpy as np

from raya.controllers.ui_controller import UIController
from raya.controllers.arms_controller import ArmsController
from raya.enumerations import ANGLE_UNIT
from raya.exceptions import RayaArmsOutOfLimits, RayaArmsExternalException

from src.static.ui.arms import *
from src.static.arms import *
from src.tools.ui import replace_key


class ArmsHandler():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui


    async def init(self):
        self.arms:ArmsController = await self.app.enable_controller('arms')
        self.arms_list = self.arms.get_arms_list()
        self.joints_lists = dict()
        for arm in self.arms_list:
            self.joints_lists[arm] = self.arms.get_joints_list(arm)
        self.predefined_poses = dict()
        for arm in self.arms_list:
            self.predefined_poses[arm] = \
                    await self.arms.get_predefined_poses_list(arm)


    async def main_display(self, default_selection=-1):
        while True:
            if default_selection == -1:
                response = await self.ui.display_choice_selector(
                        **UI_ARMS_MAIN_SELECTOR
                    )
                if response['action'] == 'back_pressed':
                    return
                selection = response['selected_option']['id']
            else:
                selection = default_selection
            if selection==1:
                await self.show_current_joints_values()
            if selection==2:
                await self.show_current_pose()
            if selection==3:
                await self.move_to_predefined_pose()
            if selection==4:
                await self.move_joint()
            if selection==5:
                await self.open_close_gripper()
            if selection==6:
                await self.cartesian_movement()

    
    # UI Methods


    async def show_current_joints_values(self):
        arm = await self.ask_arm()
        if arm is None:
            return False
        joints_info = await self.arms.get_current_joint_values(arm)
        # Actually print in UI when new tags are added
        print(joints_info)
        return True


    async def show_current_pose(self):
        arm = await self.ask_arm()
        if arm is None:
            return False
        pose = await self.arms.get_current_pose(arm)
        # Actually print in UI when new tags are added
        print(pose)
        return True


    async def move_to_predefined_pose(self, return_arm=False):
        while True:
            arm = await self.ask_arm()
            if arm is None:
                return False
            while True:
                pose = await self.ask_predefined_pose(arm)
                if pose is None:
                    break
                await self.arms.set_predefined_pose(
                        arm=arm,
                        predefined_pose=pose,
                        wait=True,
                    )
                if return_arm:
                    return arm
        return True


    async def move_joint(self):
        while True:
            arm = await self.ask_arm()
            if arm is None:
                return False
            while True:
                joint = await self.ask_arm_joint(arm)
                if joint is None:
                    break
                limit_reached = False
                while True:
                    # TODO: Add color and new line!
                    limit_warn = UI_ARMS_LIMIT_WARNING if limit_reached else ''
                    response = await self.ui.display_choice_selector(
                            **replace_key(
                                    UI_ARMS_JOINTS_CONTROLLER,
                                    arm=arm,
                                    joint=joint,
                                    limit_warn=limit_warn,
                                )
                        )
                    if response['action'] == 'back_pressed':
                        break
                    id = response['selected_option']['id']
                    current_value = await self.arms.get_current_joint_position(
                            arm=arm,
                            joint=joint,
                            units=ANGLE_UNIT.DEGREES,
                        )
                    if self.arms.is_rotational_joint(arm=arm, joint=joint):
                        increment = JOINT_INCREMENTS_ROTATIONAL[id]
                    else:
                        increment = JOINT_INCREMENTS_LINEAR[id]
                    new_value = current_value + increment
                    try:
                        await self.arms.set_joint_position(
                                arm=arm,
                                joint=joint,
                                position=new_value,
                                units=ANGLE_UNIT.DEGREES,
                                wait=True,
                            )
                        limit_reached = False
                    except (RayaArmsOutOfLimits, RayaArmsExternalException):
                        limit_reached = True
        return True


    async def open_close_gripper(self):
        while True:
            arm = await self.ask_arm()
            if arm is None:
                return False
            while True:
                response = await self.ui.display_choice_selector(
                        **replace_key(
                                UI_ARMS_OPEN_CLOSE_GRIPPE,
                                arm=arm,
                            )
                    )
                if response['action'] == 'back_pressed':
                    break
                action = response['selected_option']['id']
                await self.arms.gripper_cmd(
                        arm=arm,
                        **GRIPPER_STATES[action],
                        wait=True,
                    )
        return True


    async def cartesian_movement(self):
        arm = await self.move_to_predefined_pose(return_arm=True)
        if not arm: return False
        limit_reached = False
        while True:
            # TODO: Add color and new line!
            limit_warn = UI_ARMS_LIMIT_WARNING if limit_reached else ''
            response = await self.ui.display_choice_selector(
                    **replace_key(
                            UI_ARMS_CARTESIAN_CONTROLLER,
                            arm=arm,
                            limit_warn=limit_warn,
                        )
                )
            if response['action'] == 'back_pressed':
                break
            id = response['selected_option']['id']
            pose_increment = POSE_INCREMENTS[id]
            pose = await self.arms.get_current_pose(arm)
            for key in pose:
                pose[key] = list(np.array(pose[key]) + pose_increment[key])
            try:
                await self.arms.set_pose(
                        arm=arm, 
                        pose_dict=pose, 
                        cartesian_path=False,
                        wait=True
                    )
                limit_reached = False
            except RayaArmsExternalException:
                limit_reached = True
        return True

    
    # Helpers


    async def ask_arm(self):
        ui_data = [
                {'id':i, 'name': arm_name}
                for i, arm_name in enumerate(self.arms_list)
            ]
        response = await self.ui.display_choice_selector(
                **UI_ARMS_SELECT_ARM,
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return None
        return response['selected_option']['name']


    async def ask_arm_joint(self, arm):
        ui_data = [
                {'id':i, 'name': joint_name}
                for i, joint_name in enumerate(self.joints_lists[arm])
            ]
        response = await self.ui.display_choice_selector(
                **replace_key(UI_ARMS_SELECT_JOINT, arm=arm),
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return None
        joint = response['selected_option']['name']
        return joint


    async def ask_predefined_pose(self, arm):
        ui_data = [
                {'id':i, 'name': pose_name}
                for i, pose_name in enumerate(self.predefined_poses[arm])
            ]
        response = await self.ui.display_choice_selector(
                **replace_key(UI_ARMS_SELECT_PREDEFINED_POSE, arm=arm),
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return None
        pose = response['selected_option']['name']
        return pose

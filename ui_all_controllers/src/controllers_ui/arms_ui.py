from raya.controllers.ui_controller import UIController
from raya.controllers.arms_controller import ArmsController\

from src.static.ui.arms import *

class ArmsUI():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui

    
    async def init(self):
        self.arms:ArmsController = await self.app.enable_controller('arms')
        self.arms_list = self.arms.get_list_of_arms()
        self.joints_lists = dict()
        for arm in self.arms_list:
            self.joints_lists[arm] = self.arms.get_list_of_joints(arm)
        self.predefined_poses = dict()
        for arm in self.arms_list:
            self.predefined_poses[arm] = \
                    await self.arms.get_list_predefined_poses(arm)


    async def main_display(self):
        while True:
            response = await self.ui.display_choice_selector(
                    **UI_ARMS_MAIN_SELECTOR
                )
            if response['action'] == 'back_pressed':
                return
            selection = response['selected_option']['id']
            if selection==1:
                await self.show_current_joints_values()
            if selection==2:
                await self.show_current_pose()
            if selection==3:
                await self.move_to_predefined_pose()


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
    

    async def ask_arm_joint(self):
        arm = await self.ask_arm()
        if arm is None:
            return None, None
        ui_data = [
                {'id':i, 'name': joint_name}
                for i, joint_name in enumerate(self.joints_lists[arm])
            ]
        response = await self.ui.display_choice_selector(
                **UI_ARMS_SELECT_ARM,
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return arm, None
        joint = response['selected_option']['name']
        return arm, joint
    
    async def ask_predefined_pose(self):
        arm = await self.ask_arm()
        if arm is None:
            return None, None
        ui_data = [
                {'id':i, 'name': pose_name}
                for i, pose_name in enumerate(self.predefined_poses[arm])
            ]
        response = await self.ui.display_choice_selector(
                **UI_ARMS_SELECT_ARM,
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return arm, None
        pose = response['selected_option']['name']
        return arm, pose
    

    async def show_current_joints_values(self):
        arm = await self.ask_arm()
        if arm is None:
            return
        joints_info = await self.arms.get_current_joint_values(arm)
        # Actually print in UI when new tags are added
        print(joints_info)


    async def show_current_pose(self):
        arm = await self.ask_arm()
        if arm is None:
            return
        pose = await self.arms.get_current_pose(arm)
        # Actually print in UI when new tags are added
        print(pose)


    async def move_to_predefined_pose(self):
        arm, pose = await self.ask_predefined_pose()
        if arm is None or pose is None:
            return
        await self.arms.set_predefined_pose(
                arm=arm,
                predefined_pose=pose,
                wait=True
            )

    
    # async def move_joint(self):
    #     arm, joint = await self.ask_arm_joint()
    #     if arm is None or joint is None:
    #         return
    #     print(arm, joint)

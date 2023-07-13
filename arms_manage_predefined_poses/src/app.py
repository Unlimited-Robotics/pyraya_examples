import numpy as np

from raya.application_base import RayaApplicationBase
from raya.enumerations import ANGLE_UNIT, ARMS_MANAGE_ACTIONS
from raya.controllers.arms_controller import ArmsController

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms: ArmsController = await self.enable_controller('arms')


    async def loop(self):
        if self.list_arms:
            self.print_list_arms()
        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f'the arm name {self.arm_name} is invalid')
            self.action=ARMS_MANAGE_ACTIONS(self.action)
            self.joint_values = np.fromstring(
                    self.joint_values, sep=",").tolist()
            if (self.joint_values == '' and 
                (self.action == ARMS_MANAGE_ACTIONS.CREATE or
                    self.action == ARMS_MANAGE_ACTIONS.EDIT )):
                self.list_joints_values()
                raise ValueError(
                    f'DEFINE THE JOINTS VALUES ARRAY FOR THE PREDEFINED POSE(-j)'
                )
            units = ANGLE_UNIT.DEGREES
            if self.rad_deg:
                units = ANGLE_UNIT.RADIANS
            
            joint_values=await self.arms.manage_predefined_pose(
                arm=self.arm_name,
                name=self.predefined_pose,
                position=self.joint_values,
                action=self.action,
                units=units)
            if self.action==ARMS_MANAGE_ACTIONS.GET:
                self.log.info(f'values predefined pose {self.predefined_pose}'
                              f' are : {joint_values}')
        self.finish_app()


    async def finish(self):
        self.log.info(f'Application has finished')
    

    def get_arguments(self):
        self.arm_name = self.get_argument(
            '-a', '--arm-name',
            help='name of the arm',
            default='left_arm',
        )
        self.list_arms = self.get_flag_argument(
            '-l', '--list-arms',
            help='list available arms',
        )
        self.joint_values = self.get_argument(
            '-j','--joint-values',
            type=str,
            help=('Define the value of the joints in array format'
                  ' 0,0,0,0,0,0,0'),
            required=False,
            default= ''
        )
        self.rad_deg = self.get_flag_argument(
            '-r','--rad-deg',
            help='orientation values  in rad',
        )
        self.predefined_pose = self.get_argument(
            '-p', '--predefined-pose',
            help='name of the predefined pose',
            type=str,
            required=not self.list_arms,
            default=''
        )
        self.action = self.get_argument(
            "-c","--action",
            type=str,
            help=('Define the action to realize with the predefined pose the'
                   'options are get, create, edit or remove'),
            required=not self.list_arms,
            default=''
        )


    def print_list_arms(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(f'List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f'{c}. {arm_name}')


    async def list_predefined_poses(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(
            f'List of predefined poses of the arm: {self.arm_name}'
        )
        name_poses = await self.arms.get_list_predefined_poses(self.arm_name)
        for joint_name in name_poses:
            self.log.info(f'{joint_name}')


    def list_joints_values(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(
            f'List of joints of the arm: {self.arm_name}'
        )
        self.log.info(f'idx name\t\t\tlower limit\tupper_limit')
        units = ANGLE_UNIT.DEGREES
        if self.rad_deg:
            units = ANGLE_UNIT.RADIANS
        limits = self.arms.get_limits_of_joints(self.arm_name, units)
        name_joints = self.arms.get_state_of_arm(self.arm_name)["name"]
        for c, joint_name in enumerate(name_joints):
            self.log.info(
                f'{c}.  {joint_name}\t{limits[joint_name][0]:.2f}'
                f'\t\t{limits[joint_name][1]:.2f}'
            )

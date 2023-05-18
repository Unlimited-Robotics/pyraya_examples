import json

from raya.enumerations import ANG_UNIT
from raya.exceptions import *
from raya.controllers.arms_controller import ArmsController
from raya.application_base import RayaApplicationBase


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms : ArmsController = await self.enable_controller('arms')


    async def loop(self):
        if self.list_arms:
            self.print_list_arms()

        elif self.group:
            if not self.group in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f"the arm name {self.group} is invalid")

            await self.execute_pose()
        self.finish_app()


    async def finish(self):
        self.log.debug(f"Application has finished")
        if await self.arms.is_any_arm_in_execution():
            await self.arms.cancel_execution()


    def get_arguments(self):
        self.list_arms = self.get_flag_argument(
                '-l', '--list-arms',
                help='list available arms',
            )
        self.group = self.get_argument(
                '-g', '--group',
                help='name of the group of arms',
                default='both',
                type=str,required= False
            )
        self.arm_names = self.get_argument(
                '-a', '--arm-names',
                help='list with the name of the arms',
                default=['left_arm','right_arm'],
                type=str,list=True,required= False
            )
        self.position = self.get_argument(
                '-p', '--position',
                type=str, required=False, list=True,
                help=(
                    'Define the position values to execute,'
                    'the format for a pose should be a dict ' 
                    'like this {"x": 0.38661, "y": 0.25621, "z": 1.18}'
                    ' where xyz are the position '
                    'separate the different poses with a space'),
                default=['{"x":0.38661,"y":0.25621, "z":1.18}',
                            '{"x":0.38661,"y":-0.25621,"z":1.18}', ],
            )
        self.orientation = self.get_argument(
                '-o', '--orientation',
                type=str, required=False, list=True,
                help='Define the orientation values to execute,'
                ' the format for a pose should be a dict like this'
                ' {"roll": 0.0, "pitch": -90.0, "yaw": 0.0}, separate'
                ' the different orientation values with a space',
                default=['{"roll": 0.0}',
                         '{"roll": 0.0}']
            )
        self.rad_deg = self.get_flag_argument(
                "-r","--rad-deg",
                help='orientation values  in rad',
            )


    def print_list_arms(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info('List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f'{c}. {arm_name}')


    async def execute_pose(self):
        if len(self.position) != len(self.orientation):
            raise RayaValueException('the len of the positions'
                                     + 'and orientations must be the same')
        self.goal_poses = []
        positions = [json.loads(position) for position in self.position]
        orientations = [json.loads(orientation)
                        for orientation in self.orientation]
        
        for position, orientation in \
                zip(positions, orientations):
            pose = {}
            pose['position'] = position
            pose['orientation'] = orientation
            self.goal_poses.append(pose)

        self.log.info(f'\nPose to execute for the group {self.group}')
        self.log.info('   arm\t     |\t    pose')
        self.log.info('-----------------------------------------------------')
        for arm, pose in zip(self.arm_names, self.goal_poses):
            self.log.info(f'{arm}\t{pose["position"]}')
            self.log.info(f'       \t\t{pose["orientation"]}')
            self.log.info('-------------------------------------------------')
        units = ANG_UNIT.DEG
        if self.rad_deg:
            units = ANG_UNIT.RAD

        await self.arms.set_multi_arms_pose(
            group=self.group,
            arms= self.arm_names,
            goal_poses=self.goal_poses,
            units=units,
            callback_feedback=self.callback_feedback,
            wait=True,
        )


    def callback_feedback(self, code, error_feedback, arm, percentage):
        self.log.info(f'ARM:{arm} PERCENTAGE:{percentage:.2f}')

import numpy as np

from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController
from raya.enumerations import ANGLE_UNIT


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms: ArmsController = await self.enable_controller('arms')
        if self.list_arms:
            self.print_list_arms()
        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f'the arm name {self.arm_name} is invalid')
            if self.joint_values != '':
                self.check_values()
                await self.execute_validation(
                    self.joint_values, 
                    self.arms.get_state_of_arm(self.arm_name)[
                        "name"]
                )
            else:
                self.log.error(
                    'DEFINE THE JOINTS VALUES ARRAY TO VALIDATE(-j)'
                )
                self.list_joints_values()


    async def loop(self):
        self.finish_app()


    async def finish(self):
        print(f"\nApplication has finished")


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
            "-j","--joint-values",
            type=str,
            help=('Define the value of the joints in array format'
                  ' 0,0,0,0,0,0,0'),
            required=False,
            default= ''
        )
        self.rad_deg = self.get_flag_argument(
            "-r","--rad-deg",
            help='orientation values  in rad',
        )


    def print_list_arms(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(f'List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f"{c}. {arm_name}")


    def list_joints_values(self):
        self.log.info("")
        self.log.info("---------------------")
        self.log.info(
            f'List of joints of the arm: {self.arm_name}'
        )
        self.log.info(f'\t idx name\t\t\tlower limit\tupper_limit')
        units = ANGLE_UNIT.DEGREES
        if self.rad_deg:
            units = ANGLE_UNIT.RADIANS
        limits = self.arms.get_limits_of_joints(self.arm_name, units)
        name_joints = self.arms.get_state_of_arm(self.arm_name)['name']
        for c, joint_name in enumerate(name_joints):
            self.log.info(
                f'{c}.  {joint_name}\t{limits[joint_name][0]:.2f}\t'
                f'\t{limits[joint_name][1]:.2f}'
            )


    def check_values(self):
        self.joint_values = np.fromstring(
                    self.joint_values, sep=',').tolist()
        name_joints = self.arms.get_state_of_arm(self.arm_name)['name']
        if len(self.joint_values) != len(name_joints):
            raise ValueError(
                'Invalid length of the joint values array must '
                f'be {len(name_joints)}'
            )


    async def execute_validation(self, joints, names):
        self.log.info('')
        self.log.info('Position joints to validate')
        self.log.info('\t\t name of joint\t\t\tvalue')
        for joint, name in zip(joints, names):
            self.log.info(f"{name} \t\t {joint}")
        units = ANGLE_UNIT.DEGREES
        if self.rad_deg == True:
            units = ANGLE_UNIT.RADIANS
        await self.arms.are_joints_position_valid(
            arm=self.arm_name,
            name_joints=names,
            angle_joints=joints,
            units=units,
            callback_finish=self.callback_finish_srv,
            wait=False,
        )
        while(self.arms.are_checkings_in_progress()):
            await self.sleep(0.1)


    def callback_finish_srv(self, error, error_msg, distance):
        self.log.info('')
        if distance != '' and error == 0:
            self.log.info(
                f'FINISH VALIDATION POSITION JOINTS ARE VALID AND THE DISTANCE '
                f'FROM THE ACTUAL POSITION IS: {distance:.2f}'
            )
        else:
            self.log.error(
                'FINISH VALIDATION POSITION JOINTS ARE INVALID '
                f'{error}:{error_msg}'
            )
        self.log.info('------------')
    

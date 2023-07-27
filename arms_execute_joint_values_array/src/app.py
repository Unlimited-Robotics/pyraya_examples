import numpy as np

from raya.application_base import RayaApplicationBase
from raya.enumerations import ANGLE_UNIT
from raya.controllers.arms_controller import ArmsController


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.arms : ArmsController = await self.enable_controller('arms')

    async def loop(self):
        if self.list_arms:
            self.print_list_arms()
        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f'the arm name {self.arm_name} is invalid')
            if len(self.joint_values):
                self.check_values()
                await self.execute_position_joints()
            else:
                self.log.error(
                    f'DEFINE THE JOINTS VALUES ARRAY TO EXECUTE(-j)'
                )
                self.list_joints_values()
        self.finish_app()


    async def finish(self):
        self.log.debug(f'Application has finished')


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
            help=('Define the value of the joints in array format,'
                  ' separate each groups of joints with space'
                  ' 0,0,0,0,0,0,0,0 0.1,45,0,0,0,0,0,0'),
            required=False,
            default= [],
            list= True,
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
        name_joints = self.arms.get_state_of_arm(self.arm_name)['name']
        for c, joint_name in enumerate(name_joints):
            self.log.info(
                f'{c}.  {joint_name}\t{limits[joint_name][0]:.2f}\t\t{limits[joint_name][1]:.2f}'
            )


    def check_values(self):
        self.joint_values = [np.fromstring(
                    joints, sep=',').tolist() for joints in self.joint_values]
        name_joints = self.arms.get_state_of_arm(self.arm_name)['name']
        for joint_values in self.joint_values:
            if len(joint_values) != len(name_joints):
                raise ValueError(
                    'Invalid length of the joint values array must'
                    f' be {len(name_joints)}'
                )


    async def execute_position_joints(self):
        self.log.info('')
        self.log.info('Position joints to execute')
        self.log.info('')
        for c, joint_values in enumerate(self.joint_values):
            self.log.info(f'{c}.\t{joint_values}')

        units = ANGLE_UNIT.DEGREES
        if self.rad_deg == True:
            units = ANGLE_UNIT.RADIANS

        await self.arms.execute_joint_values_array(
            arm=self.arm_name,
            joint_values=self.joint_values,
            units=units,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=False,
        )
        while await self.arms.is_any_arm_in_execution():
            await self.sleep(0.1)


    def callback_feedback(self, code, error_feedback, arm, percentage):
        self.log.info(f'ARM:{arm} PERCENTAGE:{percentage:.2f}')


    def callback_finish(self, error, error_msg, fraction):
        self.log.info('')
        if error == 0:
            self.log.info(
                f'FINISH SUCCESSFULLY THE EXECUTION OF THE POSITION JOINTS'
            )
        else:
            self.log.error(
                f'ERROR IN THE EXECUTION NUMBER: {error}:{error_msg}'
            )
        self.log.info("------------")
        

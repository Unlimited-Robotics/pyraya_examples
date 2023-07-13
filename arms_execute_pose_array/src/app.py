import json

from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController
from raya.enumerations import ANGLE_UNIT


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms: ArmsController = await self.enable_controller('arms')


    async def loop(self):
        if self.list_arms:
            self.print_list_arms()

        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f"the arm name {self.arm_name} is invalid")
            self.check_values()
            await self.execute_poses()
        self.finish_app()


    async def finish(self):
        self.log.debug(f"Application has finished")


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
        self.poses = self.get_argument(
                    "-p", "--pose",
                    type=str,
                    help=('define the poses to check, the format '
                        'should be a json like this {“x”:0.38661,“y”:0.25621,'
                        '“z”:1.18,“r”:0,“p”:-90,“yaw”:0} where xyz are the '
                        'position and r,p,yaw are the orientation value in '
                        'euler angles representation and the different poses'
                        ' must be separated by spaces'),
                    default=[('{"x":0.38661,"y":0.25621,"z":1.18,'
                            '"r":0,"p":-90,"yaw":0}'),
                            ('{"x":0.38661,"y":0.25621,"z":1.08,'
                            '"r":0,"p":-90,"yaw":0}'),],
                    list=True
                )
        self.rad_deg = self.get_flag_argument(
                "-r","--rad-deg",
                help='orientation values  in rad',
            )
        

    def print_list_arms(self):
        self.log.info('')
        self.log.info('\n---------------------')
        self.log.info(f'List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f'{c}. {arm_name}')


    def check_values(self):
        self.poses = [json.loads(pose) for pose in self.poses]
        keys = ["x", "y", "z", "r", "p", "yaw"]
        for pose in self.poses:
            for k in pose.keys():
                if not k in keys:
                    raise ValueError(f"invalid key of the json {k}")

            for k in keys:
                if not k in pose.keys():
                    raise ValueError(f"the key {k} of the json is missing")


    async def execute_poses(self):
        self.log.info('')
        self.log.info(f'Poses to execute for the arm {self.arm_name}')
        for c, pose in enumerate(self.poses):
            self.log.info(f'{c}.\t{pose}\n')
        units = ANGLE_UNIT.DEGREES
        if self.rad_deg:
            units = ANGLE_UNIT.RADIANS

        await self.arms.execute_pose_array(
            arm=self.arm_name,
            poses=self.poses,
            units=units,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )


    def callback_feedback(self, code, error_feedback, arm, percentage):
        self.log.info(f'ARM:{arm} PERCENTAGE:{percentage:.2f}')


    def callback_finish(self, error, error_msg, fraction):
        self.log.info('')
        if error == 0:
            self.log.info(
                f'FINISH SUCCESSFULLY THE EXECUTION OF THE POSE')
        else:
            self.log.error(
                f'ERROR IN THE EXECUTION NUMBER: {error}:{error_msg}')
        self.log.info('------------')
        

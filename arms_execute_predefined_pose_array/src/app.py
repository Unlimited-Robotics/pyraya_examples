import argparse
from raya.application_base import RayaApplicationBase
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
                raise ValueError(f"the arm name {self.arm_name} is invalid")
            if self.predefined_poses:
                await self.check_predefined_pose()
                await self.execute_predefined_pose_array()
            else:
                self.log.error(
                    f'DEFINE THE PREDEFINED POSE TO EXECUTE (-p)'
                )
                await self.list_predefined_poses()
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
        self.predefined_poses = self.get_argument(
            "-p","--predefined-poses",
            type=str,
            help=('Define the predefined poses separated between them by space'
                  ' -p pre_pick home'),
            required=False,
            default= [],
            list= True
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
            self.log.info(f'{c}. {arm_name}')


    async def check_predefined_pose(self):
        self.predefined_poses = [
                pose.replace(' ', '') for pose in self.predefined_poses]
        list_predefined_poses = await self.arms.get_list_predefined_poses(
            self.arm_name
        )
        for predefined_pose in self.predefined_poses:
            if not predefined_pose in list_predefined_poses:
                await self.list_predefined_poses()
                raise ValueError(
                    f'the predefined_pose {predefined_pose} is not available '
                    'for this arm'
                )


    async def list_predefined_poses(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(
            f'List of predefined poses of the arm: {self.arm_name}'
        )
        self.log.info(f'NAME')
        name_poses = await self.arms.get_list_predefined_poses(self.arm_name)
        for c, pred_pose in enumerate(name_poses):
            self.log.info(f'{c}.{pred_pose}')


    async def execute_predefined_pose_array(self):
        self.log.info('')
        self.log.info(
            f' Start the execution of the predefined poses')
        self.log.info('')
        for c, predefined_pose in enumerate(self.predefined_poses):
            self.log.info(f'{c}.\t{predefined_pose}')
        self.log.info('')

        await self.arms.execute_predefined_pose_array(
            arm=self.arm_name,
            predefined_poses=self.predefined_poses,
            callback_feedback=self.callback_feedback,
            callback_finish=self.callback_finish,
            wait=True,
        )


    def callback_feedback(self, code, error_feedback, arm, percentage):
        self.log.info(f"ARM:{arm} PERCENTAGE:{percentage:.2f}")


    def callback_finish(self, error, error_msg, fraction):
        self.log.info('')
        if error == 0:
            self.log.info(
                f"FINISH SUCCESSFULLY THE EXECUTION OF THE PREDEFINED POSE"
            )
        else:
            self.log.error(
                f"ERROR IN THE EXECUTION NUMBER: {error}:{error_msg}"
            )
        self.log.info("------------")


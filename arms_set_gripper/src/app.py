from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController


class RayaApplication(RayaApplicationBase):

    async def setup(self):     
        self.arms:ArmsController = await self.enable_controller('arms')


    async def loop(self):
        if self.list_arms:
            self.print_list_arms()
        elif self.arm_name:
            if not self.arm_name in self.arms.get_list_of_arms():
                self.print_list_arms()
                raise ValueError(f'the arm name {self.arm_name} is invalid')
            self.check_values()
            await self.execute_gripper()
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
        self.open = self.get_flag_argument(
                '-o', '--open',
                help='open the gripper (by default it closes)',
            )
        self.pressure = self.get_argument(
                '-p', '--pressure',
                type=float,
                required=not self.open,
                help='pressure (only required when clossing)',
                default=0.0,
            )


    def print_list_arms(self):
        self.log.info('')
        self.log.info('List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f'  {c}. {arm_name}')


    def check_values(self):
        if self.pressure is None:
            raise ValueError('You must define pressure')


    async def execute_gripper(self):
        action = 'Opening' if self.open else 'Closing'
        self.log.info(f'\n{action} the gripper of the arm {self.arm_name}')
        if self.open:
            result = await self.arms.gripper_cmd(
                    arm=self.arm_name,
                    desired_position=0.0,
                    desired_pressure=self.pressure,
                    timeout=10.0,
                    wait=True,
                )
            self.action = 'OPENING'
        else:
            result = await self.arms.gripper_cmd(
                    arm=self.arm_name,
                    desired_position=1.0,
                    desired_pressure=self.pressure,
                    timeout=10.0,
                    wait=True,
                    callback_feedback=self.feedback_callback,
                )
            self.action = 'CLOSING'
        self.log.info(result)


    def feedback_callback(self, _1, _2, _3, _4, _5, _6):
        print('feedback_callback')

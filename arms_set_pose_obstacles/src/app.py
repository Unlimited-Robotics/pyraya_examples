import json

from raya.application_base import RayaApplicationBase
from raya.enumerations import ANG_UNIT
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
                raise ValueError(f"the arm name {self.arm_name} is invalid")
            self.check_values()
            await self.execute_pose()
        self.log.info('final position: '
                      f'{await self.arms.get_current_pose(self.arm_name)}')
        self.finish_app()


    async def finish(self):
        self.log.debug(f'Application has finished')
        if await self.arms.is_any_arm_in_execution():
            await self.arms.cancel_execution()


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
        self.pose = str(self.get_argument(
            "-p", "--pose",
            type=str,
            help=('define the pose to check, the format '
                  'should be a json like this {“x”:0.38661,“y”:0.25621,'
                  '“z”:1.18,“r”:0,“p”:-90,“yaw”:0} where xyz are the '
                  'position and r,p,yaw are the orientation value in '
                  'euler angles representation'),
            default=('{"x":0.38661,"y":0.25621,"z":1.18,'
                     '"r":0,"p":-90,"yaw":0}'),
        ))
        self.rad_deg = self.get_flag_argument(
            "-r", "--rad-deg",
            help='orientation values  in rad',
        )
        self.cameras = self.get_argument(
            '-c', '--cameras',
            type=str,
            required=False,
            help='cameras to use as source for obstacle detection',
            list=True,
            default= []
        )
        self.update_obstacles = self.get_flag_argument(
            '-u', '--update-obstacles',
            help= 'flag to update obstacles'
        )
        self.min_bbox_clear_obstacles = self.get_argument(
            '-minbbox', '--min-bbox-clear-obstacles',
            type=str,
            required=False,
            help=('min points array that define the minimum'
                  'corner of a bounding box to clear obstacles area'),
            list=True,
            default= []
        )
        self.max_bbox_clear_obstacles = self.get_argument(
            '-maxbbox', '--max-bbox-clear-obstacles',
            type=str,
            required=False,
            help=('max points array that define the maximum'
                  'corner of a bounding box to clear obstacles area'),
            list=True,
            default= []
        )


    def print_list_arms(self):
        self.log.info('')
        self.log.info('---------------------')
        self.log.info(f'List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            self.log.info(f'{c}. {arm_name}')


    def check_values(self):
        self.pose = json.loads(self.pose)
        self.min_bbox_clear_obstacles = [json.loads(
                min_bbox) for min_bbox in self.min_bbox_clear_obstacles]
        self.max_bbox_clear_obstacles = [json.loads(
                max_bbox) for max_bbox in self.max_bbox_clear_obstacles]
        keys = ["x", "y", "z", "r", "p", "yaw"]
        for k in self.pose.keys():
            if not k in keys:
                raise ValueError(f'invalid key of the json {k}')

        for k in keys:
            if not k in self.pose.keys():
                raise ValueError(f'the key {k} of the json is missing')


    async def execute_pose(self):
        self.log.info('')
        self.log.info(f'Pose to execute for the arm {self.arm_name}')
        self.log.info('key\tvalue')
        for key in self.pose:
            self.log.info(f'{key}\t{self.pose[key]}')
        units = ANG_UNIT.DEG
        if self.rad_deg:
            units = ANG_UNIT.RAD

        await self.arms.set_pose(
            arm=self.arm_name,
            x=self.pose["x"],
            y=self.pose["y"],
            z=self.pose["z"],
            roll=self.pose["r"],
            pitch=self.pose["p"],
            yaw=self.pose["yaw"],
            units=units,
            use_obstacles=True,
            cameras=self.cameras,
            update_obstacles=self.update_obstacles,
            min_bbox_clear_obstacles=self.min_bbox_clear_obstacles,
            max_bbox_clear_obstacles=self.max_bbox_clear_obstacles,
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
                f'FINISH SUCCESSFULLY THE EXECUTION OF THE POSE')
        else:
            self.log.error(
                f'ERROR IN THE EXECUTION NUMBER: {error}:{error_msg}')
        self.log.info("------------")
        

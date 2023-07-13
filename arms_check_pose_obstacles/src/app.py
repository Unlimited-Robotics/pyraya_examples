import json

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
                raise ValueError(f"the arm name {self.arm_name} is invalid")
            self.check_values()
            await self.execute_validation()


    async def loop(self):
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
        self.log.info("\n---------------------")
        self.log.info(f'List of available arms')
        for c, arm_name in enumerate(self.arms.get_list_of_arms()):
            print(f"{c}. {arm_name}")


    def check_values(self):
        self.pose = json.loads(self.pose)
        self.min_bbox_clear_obstacles = [json.loads(
                min_bbox) for min_bbox in self.min_bbox_clear_obstacles]
        self.max_bbox_clear_obstacles = [json.loads(
                max_bbox) for max_bbox in self.max_bbox_clear_obstacles]

        keys = ["x", "y", "z", "r", "p", "yaw"]
        for k in self.pose.keys():
            if not k in keys:
                raise ValueError(f"invalid key of the json {k}")

        for k in keys:
            if not k in self.pose.keys():
                raise ValueError(f"the key {k} of the json is missing")


    async def execute_validation(self):
        self.log.info(f"Pose to validate for the arm {self.arm_name}")
        self.log.info("key\tvalue")
        for key in self.pose:
            self.log.info(f"{key}\t\t{self.pose[key]}")

        units = ANGLE_UNIT.DEGREES
        if self.rad_deg:
            units = ANGLE_UNIT.RADIANS

        await self.arms.is_pose_valid(
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
            callback_finish=self.callback_finish_srv,
            wait=False,
        )
        while (self.arms.are_checkings_in_progress()):
            await self.sleep(0.1)


    def callback_finish_srv(self, error, error_msg, distance, fraction, 
                            final_position, start_position):
        self.log.info("")
        self.log.info("callback_finish")
        if error == 0:
            self.log.info('callback result:  distance '
                      f'{distance:.2f}, fraction {fraction:.2f}')
            self.log.info(
                f'final_position {[f"{n:.2f}"for n in final_position]}')
            self.log.info(
                f'start_position {[f"{n:.2f}"for n in start_position]}')
        else:
            self.log.error(
                f'FINISH VALIDATION POSITION JOINTS ARE INVALID, {error}:'
                f'{error_msg}'
            )
        self.log.info("------------")

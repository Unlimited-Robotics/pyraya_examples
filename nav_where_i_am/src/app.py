import cv2
import math

from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating, RayaNavInvalidGoal
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')


    async def loop(self):
        self.list_of_maps = await self.navigation.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        robot_localized = await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=self.cb_set_map_feedback,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Using map \'{self.map_name}\'')
        robot_pix_rad = await self.navigation.get_position(
                pos_unit=POS_UNIT.PIXEL, 
                ang_unit=ANG_UNIT.RAD
            )
        robot_met_deg = await self.navigation.get_position(
                pos_unit=POS_UNIT.METERS, 
                ang_unit=ANG_UNIT.DEG
            )
        self.log.info((
                f'Robot location (pixels): {robot_pix_rad[0]} {robot_pix_rad[1]}'
            ))
        self.log.info((
                f'Robot location (meters): {robot_met_deg[0]} {robot_met_deg[1]}'
            ))
        self.log.info((
                f'Robot orientation (radians): {robot_pix_rad[2]}'
            ))
        self.log.info((
                f'Robot orientation (degress): {robot_met_deg[2]}'
            ))
        self.finish_app()
        

    async def finish(self):
        try:
            await self.navigation.cancel_navigation()
        except (RayaNavNotNavigating, AttributeError):
            pass
        self.log.info('Finish app called')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )


    def cb_set_map_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'set map feedback: {feedback_code} {feedback_msg}')

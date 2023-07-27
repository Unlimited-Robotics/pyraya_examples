from raya.enumerations import *
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        robot_localized = await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=None,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Localized. Using map \'{self.map_name}\'')

        localization_meters = await self.navigation.get_position(
                pos_unit=POSITION_UNIT.METERS,
                ang_unit = ANGLE_UNIT.RADIANS
            )
        localization_pixels = await self.navigation.get_position(
                pos_unit=POSITION_UNIT.PIXELS,
                ang_unit = ANGLE_UNIT.DEGREES
            )
        self.log.info((
                'Robot coordinates (meters)= '
                f'\'{localization_meters[:2]}\''
            ))
        self.log.info((
                'Robot coordinates (pixels)= '
                f'\'{localization_pixels[:2]}\''
            ))
        self.log.info((
                'Robot orientation (radians)= '
                f'\'{localization_meters[2]}\''
            ))
        self.log.info((
                'Robot orientation (degrees)= '
                f'\'{localization_pixels[2]}\''
            ))


    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('App finished')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )

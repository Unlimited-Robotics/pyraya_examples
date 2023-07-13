from raya.exceptions import RayaNavNotNavigating
from raya.application_base import RayaApplicationBase
from raya.enumerations import POSITION_UNIT, ANGLE_UNIT
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.nav: NavigationController = \
                await self.enable_controller('navigation')
        self.list_of_maps = await self.nav.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((f'Setting map: {self.map_name}. '
                       'Waiting for the robot to get localized'))
        robot_localized = await self.nav.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.status = await self.nav.get_status()
        self.log.info(f'status: {self.status}')
        self.location = await self.nav.get_location(
                location_name=self.location_name,
                map_name=self.map_name, 
                pos_unit=POSITION_UNIT.PIXELS
            )
        goal_x, goal_y, goal_yaw = self.location[0], self.location[1], 0.0
        self.log.warn(f'New goal received {goal_x, goal_y, goal_yaw}')
        await self.nav.navigate_to_location(
                location_name = self.location_name,
                callback_feedback = self.cb_nav_feedback, 
                callback_finish = self.cb_nav_finish, 
                wait=True
            )
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        try:
            await self.nav.cancel_navigation()
        except RayaNavNotNavigating:
            pass
        self.log.info('Finish app called')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the map',
                required=True
            )
        self.location_name = self.get_argument(
                '-l', '--location-name',
                type=str,
                help='location name',
                required=False,
                default='kitchen'
            )
        
    
    def cb_nav_finish(self, error, error_msg):
        self.log.info(f'Navigation final state: {error} {error_msg}')
        if error != 0 and error != 18:
            self.log.error('Error in navigation')
            self.finish_app()


    def cb_nav_feedback(self,  error, error_msg, distance_to_goal, speed):
        self.log.info(f'Navigation feedback {distance_to_goal} {speed}')

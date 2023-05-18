from raya.exceptions import RayaNavNotNavigating
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.nav: NavigationController = \
                await self.enable_controller('navigation')       
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        robot_localized = await self.nav.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=self.cb_set_map_feedback,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Using map \'unity_apartment\'')
        self.goal_zone = self.zone_name
        self.log.warn(f'New goal received zone {self.goal_zone}')
        await self.nav.navigate_to_zone( 
                zone_name=self.goal_zone,
                to_center=True,
                callback_feedback = self.cb_nav_feedback,
                callback_finish = self.cb_nav_finish,
                wait=False,
            )


    async def loop(self):
        if await self.nav.is_in_zone(zone_name=self.goal_zone):
            self.log.warn(f'Robot in zone')
            if not self.go_center:
                await self.nav.cancel_navigation()
        else:
            pass
            #self.log.info((f'Robot not in zone'))
        await self.sleep(0.3)


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
                help='name of the new map',
                required=True
            )
        self.zone_name = self.get_argument(
                '-z', '--zone-name',
                type=str,
                help='name of zone to navigate to',
                required=False,
                default='room1'
            )
        self.go_center = self.get_flag_argument(
                '-c', '--go-center',
                help='use if you want to navigate to the center of the zone',
            )


    def cb_nav_finish(self, error, error_msg):
        self.log.info(f'Navigation final state: {error} {error_msg}')
        if error != 0 and error != 18:
            self.log.error('Error in navigation')
            self.finish_app()


    def cb_nav_feedback(self, error, error_msg, distance_to_goal, speed):
        self.log.info(f'Navigation feedback {distance_to_goal} {speed}')

    
    def cb_set_map_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'set map feedback: {feedback_code} {feedback_msg}')

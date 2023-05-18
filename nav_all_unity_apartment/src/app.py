from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaUnableToComputePath, RayaNavLocationNotFound
from raya.exceptions import RayaNavMappingDisabled, RayaNavLocationAlreadyExist
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.list_of_maps = await self.navigation.get_list_of_maps()
        self.log.info(f'Available maps = \'{self.list_of_maps}\'')
        self.map_image, self.map_info = \
                await self.navigation.get_map(map_name='unity_apartment')
        self.log.info(f'Unity_apartment info = \'{self.map_info}\'')
        self.navigation_status = await self.navigation.get_status()
        self.log.info((
                'Current navigation status ='
                f'\'{self.navigation_status}\''
            ))
        try:
            await self.navigation.start_mapping(map_name='test1001')
        except RayaNavMappingDisabled:
            self.log.error(f'unable to start mapping in simulation')
        try: 
            await self.navigation.delete_location( 
                    location_name='test003', 
                    map_name='unity_apartment'
                )
            self.log.info(f'Location deleted')
        except RayaNavLocationNotFound:
            self.log.error(f'Unable to delete location: location not found.')
        try: 
            await self.navigation.save_location( 
                    x=1.0, 
                    y=0.5, 
                    angle=1.0,
                    location_name='test002', 
                    pos_unit=POS_UNIT.METERS, 
                    ang_unit=ANG_UNIT.RAD, 
                    map_name='unity_apartment'
                )
            self.log.info(f'Location saved')
        except RayaNavLocationAlreadyExist:
            self.log.error('Unable to save location: location already exists.')
        robot_localized = await self.navigation.set_map(
                map_name='unity_apartment', 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=self.cb_set_map_feedback,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Using map \'unity_apartment\'')

        self.location = await self.navigation.get_location(
                location_name='kitchen', 
                map_name='unity_apartment',
                pos_unit=POS_UNIT.PIXEL
            )
        self.log.info(f'kitchen info= {self.location}')

        locations = await self.navigation.get_locations_list(
                map_name='unity_apartment'
            )
        self.log.info(f'list of locations = {locations}')

        locations_info = await self.navigation.get_locations(
                map_name='unity_apartment'
            )
        self.log.info(f'info of locations = {locations_info}')

        zones_list = await self.navigation.get_zones(
                map_name='unity_apartment'
            )
        self.log.info(f'list of zones = {zones_list}')

        zones_info = await self.navigation.get_zones_list(
                map_name='unity_apartment'
            )
        self.log.info(f'info of zones = {zones_info}')

        kitchen_center = await self.navigation.get_zone_center(
                zone_name='kitchen'
            )
        self.log.info(f'kitchen center = {kitchen_center}')

        on_kitchen = await self.navigation.is_in_zone(
                zone_name='kitchen'
            )
        self.log.info(f'Robot is on kitchen = {on_kitchen}')

        robot_position = await self.navigation.get_position(
                pos_unit=POS_UNIT.PIXEL, 
                ang_unit=ANG_UNIT.DEG
            )
        self.log.info(f'Robot position = {robot_position}')
        self.log.info('Navigating to kitchen')
        try:
            await self.navigation.navigate_to_location(
                    location_name='kitchen',
                    callback_feedback=self.cb_nav_feedback, 
                    callback_finish=self.cb_nav_finish, 
                    wait=True
                )
        except RayaUnableToComputePath:
            self.log.error('Unable to compute path to kitchen')
        self.log.info('Navigating to initial zone')
        await self.navigation.navigate_to_zone(
                zone_name='initial_zone',
                to_center=True,
                callback_feedback=self.cb_nav_feedback, 
                callback_finish=self.cb_nav_finish, 
                wait=False
            )
        while not await self.navigation.is_in_zone(zone_name='initial_zone'): 
            await self.sleep(0.5)
            self.log.info('Navigating to zone...')
        self.log.info('Robot in zone')
        await self.navigation.cancel_navigation()
        self.log.info('Navigation canceled')
        await self.sleep(0.5)
        await self.navigation.navigate_to_position( 
                x=0.0, 
                y=1.0, 
                angle=90.0, 
                pos_unit=POS_UNIT.METERS, 
                ang_unit=ANG_UNIT.RAD,
                callback_feedback=self.cb_nav_feedback,
                callback_finish=self.cb_nav_finish,
                wait=True,
            )
        await self.sleep(0.5)
        await self.navigation.go_to_angle( 
                angle_target=180, 
                angular_velocity=1.0, 
                ang_unit=ANG_UNIT.DEG,
                callback_feedback=self.cb_go_to_angle_feedback,
                callback_finish=self.cb_go_to_angle_finish,
                wait=True,
            )
        await self.sleep(0.5)
        path_to_zero_position = await self.navigation.check_path_to_goal(
                x=0.0, 
                y=0.0, 
                in_map_coordinates=True
            )
        self.log.info((
                'Exists path to zero coordinate =' 
                f'{path_to_zero_position}'
            ))
        await self.navigation.navigate_close_to_position( 
                x=1.42, 
                y=-2.96, 
                min_radius=0.4,
                max_radius=0.8,
                pos_unit=POS_UNIT.METERS,
                callback_feedback=self.cb_nav_feedback,
                callback_finish=self.cb_nav_finish,
                wait=True,
            )
        self.log.info('Final position reached')
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        self.log.info('Trying to cancel running navigation')
        try:
            await self.navigation.cancel_navigation()
        except Exception as e:
            self.log.warn('Robot is not navigating...')
        self.log.info('App finished')


    def cb_nav_finish(self, error, error_msg):
        self.log.info(f'Navigation final state: {error} {error_msg}')
        if error != 0 and error != 18:
            self.log.error('Error in navigation')
            self.finish_app()


    def cb_nav_feedback(self, error, error_msg, distance_to_goal, speed):
        self.log.info(f'Navigation feedback {distance_to_goal} {speed}')
    

    def cb_set_map_finish(self, error, error_msg):
        self.log.info(f'set_map final state: {error} {error_msg}')


    def cb_set_map_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'set map feedback: {feedback_code} {feedback_msg}')


    def cb_go_to_angle_finish(self, error, error_msg, interrupted, obstacle):
        self.log.info((
                'go to angle final state:' 
                f'error :{error} {error_msg}' 
                f'interrupted: {interrupted}' 
                f'obstacle type: {obstacle}'
            ))


    def cb_go_to_angle_feedback(self,  
                feedback_code, 
                feedback_msg, 
                angle_left, 
                nearby_obstacle
            ):
        self.log.info((
                f'go to angle feedback: {feedback_code} {feedback_msg}'
                f'angle left: {angle_left} obstacle: {nearby_obstacle}'
            ))

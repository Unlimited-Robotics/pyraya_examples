from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaNavNotNavigating
from raya.controllers.navigation_controller import NavigationController


MINI_GARY = [
        [-0.25,  0.28],
        [ 0.25,  0.28],
        [ 0.25, -0.28],
        [-0.25, -0.28]
    ]


GARY_FOOTPRINT = [
        [-0.25,  0.34],
        [ 0.25,  0.34],
        [ 0.25, -0.34],
        [-0.25, -0.34]
    ]


floors_data = [
        {'map_name': 'floor.01', 'locations': ['door', 'initial_position']},
        {'map_name': 'floor.03', 'locations': ['reception', 'initial_position']},
    ]


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.localized = False
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        await self.navigation.update_robot_footprint(points=MINI_GARY)
        list_of_maps = await self.navigation.get_list_of_maps()
        for floor in floors_data:
            if not floor['map_name'] in list_of_maps:
                self.log.error(f'Map {floor["map_name"]} not found')
                self.finish_app()
        self.map_index = 0
        self.location_index = 0
        self.current_map = floors_data[self.map_index]
        self.goal_location = self.current_map['locations'][self.location_index]
        self.load_map_required = True
        

    async def loop(self):
        if self.load_map_required:
            self.log.info((
                    f'Setting map: {self.current_map["map_name"]}. '
                    'Waiting for the robot to get localized'
                ))
            localized = await self.navigation.set_map(
                    map_name=self.current_map['map_name'], 
                    wait_localization=True, 
                    wait = True,
                    callback_feedback=self.cb_set_map_feedback,
                    callback_finish=self.cb_set_map_finish
                )        
            if not localized:
                self.log.error(f'Robot couldn\'t localize itself')
                self.finish_app()
            self.log.info(f'Localized in map \'{self.current_map["map_name"]}\'')
            self.load_map_required = False
            self.navigation_required = True
        if self.navigation_required:
            self.log.info(f'Navigating to {self.goal_location}')
            await self.navigation.navigate_to_location( 
                    location_name = self.goal_location, 
                    callback_feedback = self.cb_nav_feedback,
                    callback_finish = self.cb_nav_finish,
                    options={"behavior_tree": "navigate_and_replan_if_needed"},
                    wait=False,
                )
            self.navigation_required = False
        await self.sleep(1)


    async def finish(self):
        try:
            await self.navigation.cancel_navigation()
        except (RayaNavNotNavigating, AttributeError):
            pass
        self.log.info('Finish app called')


    def get_arguments(self):
        self.enable_repeats = self.get_flag_argument(
                '-r', '--enable_repeats',
                help='use if you want to repeat the sequences',
            )


    def cb_set_map_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'set map feedback: {feedback_code} {feedback_msg}')


    def cb_set_map_finish(self, error, error_msg):
        if error != 0:
            self.log.error(f'set map finish: {error} {error_msg}')
            self.finish_app()
        

    def cb_nav_finish(self, error, error_msg):
        if error==0:
            self.log.info(f'Navigation Finish: {error} {error_msg}')
            self.location_index += 1
            if self.location_index > len(floors_data[0]['locations']) -1:
                self.restart_status()
            else:
                self.navigation_required = True
            self.goal_location = self.current_map['locations'][self.location_index]
        else:
            self.log.info(f'Navigation Error: {error} {error_msg}')
            self.finish_app()

    def cb_nav_feedback(self, error, error_msg, distance_to_goal, speed):
        pass
        #self.log.info((
        #        'Navigation Feedback: \n'
        #        f'error = {error} \n error_msg={error_msg} \n' 
        #        f'distance_to_goal = {distance_to_goal}, speed = {speed}'
        #    ))


    def restart_status(self):
        self.location_index = 0
        if self.map_index >= len(floors_data) -1:
            if self.enable_repeats:
                self.map_index = 0
            else:
                self.finish_app()
        else:
            self.map_index += 1
        self.current_map = floors_data[self.map_index]
        self.load_map_required = True

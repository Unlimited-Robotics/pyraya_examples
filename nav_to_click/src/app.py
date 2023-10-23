import cv2
import math

from raya.application_base import RayaApplicationBase
from raya.enumerations import POSITION_UNIT, ANGLE_UNIT
from raya.exceptions import RayaNavNotNavigating, RayaNavInvalidGoal
from raya.controllers.navigation_controller import NavigationController


GARY_FOOTPRINT = [
        [-0.25,  0.35],
        [ 0.25,  0.35],
        [ 0.25, -0.35],
        [-0.25, -0.35]
    ]
GARY_AND_TRAY_FOOTPTINT = [
        [-0.28,  0.37],
        [ 0.60,  0.37],
        [ 0.60, -0.37],
        [-0.28, -0.37]
    ]


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.flag = False
        self.counter = 0
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        await self.navigation.update_robot_footprint(points=GARY_FOOTPRINT)
        self.list_of_maps = await self.navigation.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        robot_localized = await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=60.0,
                callback_feedback=self.cb_set_map_feedback,
                callback_finish=self.cb_set_map_finish
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Using map \'{self.map_name}\'')
        self.map_image, self.map_info = await self.navigation.get_map(
                map_name=self.map_name
            )
        try:
            await self.navigation.enable_speed_zones()
        except:
            self.log.info(f'No speed zones available')
        cv2.namedWindow('map')
        cv2.setMouseCallback('map', self.get_click_coordinates)
        self.click_down = False
        self.point_down = (0,0)
        self.point_mouse = (0,0)
        self.new_goal = (0,0,0)
        self.new_flag = False

        self.log.info('')
        self.log.info('Controls:')
        self.log.info('  - ESC: Exit')
        self.log.info('  - Click and hold: set position and orientation')
        self.log.info('  - C: Cancel current navigation')


    async def loop(self):
        robot_position = await self.navigation.get_position(
                pos_unit=POSITION_UNIT.PIXELS, 
                ang_unit=ANGLE_UNIT.RADIANS
            )
        img = self.draw(robot_position)
        cv2.imshow('map', img)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            self.finish_app()
        if key == ord('C') or key == ord('c'):
            if self.navigation.is_navigating():
                self.log.info('Cancelling current navigation')
                try:
                    await self.navigation.cancel_navigation()
                except:
                    self.log.error('No navigation in execution...')
        if self.new_flag:
            if self.navigation.is_navigating():
                self.log.warn('Cancel current goal before send a new one.')
                self.new_flag = False
            else:
                self.log.warn(f'New goal received {self.new_goal}')
                try:
                    await self.navigation.navigate_to_position( 
                        # x=0.0, y=1.0, angle=90.0, pos_unit = POSITION_UNIT.METERS, 
                        x=float(self.new_goal[0]), 
                        y=float(self.new_goal[1]), 
                        angle=self.new_goal[2], pos_unit = POSITION_UNIT.PIXELS, 
                        ang_unit = ANGLE_UNIT.RADIANS,
                        callback_feedback = self.cb_nav_feedback,
                        callback_finish = self.cb_nav_finish,
                        #options={"behavior_tree": "navigate_and_move_back"},
                        wait=False,
                    )
                except RayaNavInvalidGoal:
                    self.log.warn(f'Invalid goal')
                self.new_flag = False


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


    def cb_set_map_finish(self, error, error_msg):
        if error != 0:
            self.log.error(f'set map finish: {error} {error_msg}')
            self.finish_app()


    def cb_nav_finish(self, error, error_msg):
        self.log.info(f'Navigation Finish: {error} {error_msg}')


    def cb_nav_feedback(self, error, error_msg, distance_to_goal, speed):
        self.log.info((
                'Navigation Feedback: \n'
                f'error = {error} \n error_msg={error_msg} \n' 
                f'distance_to_goal = {distance_to_goal}, speed = {speed}'
            ))


    def draw(self, robot_position):
        img = self.map_image.copy()
        x_pixel  = int(robot_position[0])
        y_pixel  = int(robot_position[1])
        rotation = robot_position[2]
        x_line   =  x_pixel + int(7 * math.cos(-rotation))
        y_line   =  y_pixel + int(7 * math.sin(-rotation))
        cv2.circle(
                img=img, 
                center=(x_pixel, y_pixel), 
                radius=8, 
                color=(255,0,0), 
                thickness=2
            )      
        cv2.line(
                img=img, 
                pt1=(x_pixel, y_pixel), 
                pt2=(x_line, y_line), 
                color=(0,0,255), 
                thickness=4
            )
        if self.click_down:
            cv2.arrowedLine(
                    img=img, 
                    pt1=self.point_down, 
                    pt2=self.point_mouse, 
                    color=(0,150,0), 
                    thickness=3
                )
        return img


    def get_click_coordinates(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.point_down = (x, y)
            self.point_mouse = (x, y)
            self.click_down = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.new_goal = (
                    self.point_down[0],
                    self.point_down[1],
                    -self.angle_between_points(
                            self.point_down, self.point_mouse
                        )
                )
            self.new_flag = True
            self.click_down = False
        elif event == cv2.EVENT_MOUSEMOVE:
            self.point_mouse = (x, y)

    
    def angle_between_points(self, p1, p2):
        return math.atan2(p2[1]-p1[1], p2[0]-p1[0])

#python3 nav_to_charger_refactored -m ur_office1 -ts 0.0865 -idl 4 -idr 5 -dbt 0.35 -ix -3.799 -iy -4.123 -ia -0.828 -dt 0.5 -me 0.06
import os
import math
from enum import IntEnum
import tf_transformations
from datetime import datetime

from raya.enumerations import *
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.controllers.motion_controller import MotionController
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.sensors_controller import SensorsController
from raya.controllers.lidar_controller import LidarController
from raya.controllers.fleet_controller import FleetController
from raya.enumerations import POSITION_UNIT, ANGLE_UNIT
from raya.handlers.cv.tags_detector_handler import TagsDetectorHandler
from raya.exceptions import RayaNavNotNavigating, RayaNavInvalidGoal

from src.modules.lidar_utils import LidarUtils
from src.modules.approach_to_goal import ApproachToGoal


class CurrentState(IntEnum):
    IDLE                            = 0
    SETTING_FIRST_GOAL              = 1
    NAVIGATING_TO_INITIAL_POSITION  = 2
    DETECTING_TAG                   = 3
    NAVIGATING_TO_TAG               = 4
    ADJUSTING_LOCATION              = 5
    CONNECTING_TO_CHARGER           = 6
    FINISHING_APP                   = 99
    TESTING                         = 100


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.min_angle_lidar = math.radians(0.0 - self.ANGLE_TO_DETECT_WALL)
        self.max_angle_lidar = math.radians(0.0 + self.ANGLE_TO_DETECT_WALL)
        self.fleet: FleetController = await self.enable_controller('fleet')
        self.log.info(f'Fleet activated')
        self.nav: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info(f'Navigation activated')
        self.lidar: LidarController = await self.enable_controller('lidar')
        self.log.info(f'Lidar activated')
        self.lidar_utils = LidarUtils(self)
        robot_localized = await self.nav.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.state:CurrentState = CurrentState.IDLE
        
        self.motion: MotionController = await self.enable_controller('motion')
        self.log.info(f'Motion activated')
        self.sensors: SensorsController = \
                await self.enable_controller('sensors')
        self.log.info(f'Sensors activated')
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.log.info(f'Cameras activated')
        self.cv: CVController = await self.enable_controller('cv')
        self.log.info(f'CV activated')
        await self.cameras.enable_color_camera(self.CAMERA)
        model_params = {
                'families': self.TAG_FAMILY,
                'nthreads': 4,
                'quad_decimate': 2.0,
                'quad_sigma': 0.0,
                'decode_sharpening': 0.25,
                'refine_edges': 1,
                'tag_size': self.TAG_SIZE,
            }
        self.detector: TagsDetectorHandler = await self.cv.enable_model(
                name='apriltags',
                source=self.CAMERA,
                model_params=model_params,
            )
        self.__initial_time = None
        self.__waiting_detection = False
        self.__detection_tag_left = None
        self.__navigation_error = None
        self.approach_to_goal = ApproachToGoal(
                app=self,
                id_tag1=self.TAG_IDS[0], 
                id_tag2=self.TAG_IDS[1], 
                distance_to_tag=self.FINAL_DISTANCE_TO_TAG, 
                error_threshold=self.ERROR_THRESHOLD,
                detector=self.detecto,
            ) 
        if not self.testing:
            self.state:CurrentState = CurrentState.SETTING_FIRST_GOAL
        else:
            self.log.info(f'TESTING MODE ON')
            self.state:CurrentState = CurrentState.TESTING


    async def loop(self):
        await self.sleep(0.1)
        if self.state == CurrentState.SETTING_FIRST_GOAL:
            try:
                await self.nav.navigate_to_position( 
                        x=self.x_initial,
                        y=self.y_initial,
                        angle=self.angle_initial,
                        pos_unit = POSITION_UNIT.METERS, 
                        ang_unit = ANGLE_UNIT.RADIANS,
                        wait=False,
                        callback_finish = self.cb_nav_finish,
                    )
            except RayaNavInvalidGoal:
                await self.finish_with_error('Invalid goal')
            self.log.info(f'Navigating to initial position')
            self.state:CurrentState = \
                    CurrentState.NAVIGATING_TO_INITIAL_POSITION
        elif self.state == CurrentState.NAVIGATING_TO_INITIAL_POSITION:
            if self.__navigation_error:
                await self.finish_with_error((
                        'Navigation failed: '
                        f'{self.__navigation_error[1]}'
                    ))
            if not self.nav.is_navigating() and not self.__navigation_error:
                self.detector.set_detections_callback(
                        callback=self.tags_cb,
                        as_dict=True,
                        call_without_detections=True,
                    )
                self.__waiting_detection = True
                self.log.info(f'Detecting tag')
                await self.sleep(0.6)
                self.__initial_time = datetime.now()
                self.state:CurrentState = CurrentState.DETECTING_TAG
        elif self.state == CurrentState.DETECTING_TAG:
            time_passed = datetime.now() - self.__initial_time
            time_detecting = (time_passed).total_seconds()
            if time_detecting > self.DETECT_TIMEOUT:
                await self.finish_with_error('Couldn\'t find laundry cart')
            if self.__detection_tag_left:
                self.log.info(f'Cart detected')
                if self.nav_to_tag:
                    tag_goal_coordinates = await self.get_goal_to_tag(
                            detection=self.__detection_tag_left, 
                            distance_between_tags=self.DISTANCE_BETWEEN_TAGS, 
                            distance_to_tag=self.DISTANCE_TO_TAG,
                        )
                    if tag_goal_coordinates:
                        self.log.info(f'Navigating to tag')
                        await self.nav.navigate_to_position( 
                                x=tag_goal_coordinates[0], 
                                y=tag_goal_coordinates[1], 
                                angle=tag_goal_coordinates[2], 
                                pos_unit=POSITION_UNIT.METERS, 
                                ang_unit=ANGLE_UNIT.RADIANS,
                                wait=False,
                                callback_finish=self.cb_nav_finish,
                            )
                        self.state = CurrentState.NAVIGATING_TO_TAG
                    else:
                        self.__detection_tag_left = None
                        self.__waiting_detection = True 
                else:
                    self.state = CurrentState.NAVIGATING_TO_TAG
        elif self.state == CurrentState.NAVIGATING_TO_TAG:
            if self.__navigation_error:
                await self.finish_with_error((
                        f'Navigation failed: {self.__navigation_error[1]}'
                    ))
            if not self.nav.is_navigating() and not self.__navigation_error:
                self.log.info(f'Approaching to charger')
                self.approach_to_goal.enable()
                self.enable_odom_camera()
                self.create_task(
                        name='adjust_position',     
                        afunc=self.approach_to_goal.approach_between_tags,
                    )
                self.state = CurrentState.ADJUSTING_LOCATION
        elif self.state == CurrentState.ADJUSTING_LOCATION:
            if not self.is_task_running('adjust_position'):
                self.approach_to_goal.disable()
                response_adj_position = self.pop_task_return('adjust_position')
                if response_adj_position:
                    await self.sleep(0.1)
                    await self.motion.set_velocity(
                            x_velocity=0.1,
                            y_velocity=0.0,
                            angular_velocity=0.0, 
                            duration=8.0, 
                            ang_unit=ANGLE_UNIT.RADIANS,
                            wait=False,
                        )
                    self.log.info(f'Moving checking lidar')
                    self.state = CurrentState.MOVING_READING_LIDAR
                else:
                   self.log.error(f'Error adjusting position')
                   self.state = CurrentState.FINISHING_APP
        elif self.state == CurrentState.MOVING_READING_LIDAR:
            lidar_current_data = self.lidar.get_raw_data()
            lidar_data = await self.lidar_utils.get_lidar_between(
                    lidar_data=lidar_current_data, 
                    lower_angle=self.min_angle_lidar, 
                    upper_angle=self.max_angle_lidar,
                )
            distance_to_wall = \
                    await self.lidar_utils.get_distance_to_line(lidar_data)
            if distance_to_wall <= 0.5:
                await self.motion.cancel_motion()
                await self.motion.set_velocity(
                        x_velocity=0.010708542997247194,
                        y_velocity=0.0,
                        angular_velocity=0.0, 
                        duration=5.2, 
                        ang_unit=ANGLE_UNIT.RADIANS,
                        wait=False,
                    )
                self.log.info(f'Connecting to charger')
                self.state = CurrentState.CONNECTING_TO_CHARGER
            self.log.info(f'Distance to wall = {distance_to_wall}')
        elif self.state == CurrentState.CONNECTING_TO_CHARGER:
            lidar_current_data = self.lidar.get_raw_data()
            lidar_data = await self.lidar_utils.get_lidar_between(
                    lidar_data=lidar_current_data, 
                    lower_angle=self.min_angle_lidar, 
                    upper_angle=self.max_angle_lidar,
                )
            distance_to_wall = \
                    await self.lidar_utils.get_distance_to_line(lidar_data)
            
            if not self.motion.is_moving():
                self.log.warn(f'Canceling motion due to timeout')
                self.state = CurrentState.FINISHING_APP
            elif distance_to_wall <= self.STOP_DISTANCE:
                await self.motion.cancel_motion()
                self.log.warn(f'Canceling motion due to lidar threshold')
                self.state = CurrentState.FINISHING_APP
        elif self.state == CurrentState.FINISHING_APP:
            self.log.warn(f'Finishing app')
            self.finish_app()
        elif self.state == CurrentState.TESTING:
            lidar_current_data = self.lidar.get_raw_data()
            lidar_data = await self.lidar_utils.get_lidar_between(
                    lidar_data=lidar_current_data, 
                    lower_angle=self.min_angle_lidar, 
                    upper_angle=self.max_angle_lidar,
                )
            distance_to_wall = \
                    await self.lidar_utils.get_distance_to_line(lidar_data)
            self.log.warn(f'Canceling motion due to lidar threshold')
               

    async def finish(self):
        try:
            await self.nav.cancel_navigation()
        except (RayaNavNotNavigating, AttributeError, Exception) as e:
            self.log.warn(f'Error canceling navigation: {e}')
        try:
            self.disable_odom_camera()
        except Exception as e:
            self.log.warn(f'Error trying to disable camera: {e}')
        self.log.warn(f'Application has finished')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )
        self.tags_size = self.get_argument(
                '-ts', '--tags-size',
                type=float,
                help='size of the apriltags on goal',
                required=True
            )
        self.left_id = self.get_argument(
                '-idl', '--left-tag-id',
                type=int,
                help='left apriltag ID',
                required=True
            )
        self.right_id = self.get_argument(
                '-idr', '--right-tag-id',
                type=int,
                help='right apriltag ID',
                required=True
            )
        self.dist_betw_tags = self.get_argument(
                '-dbt', '--dist-between-tags',
                type=float,
                help='distance between left and right tags',
                required=True
            )
        self.x_initial = self.get_argument(
                '-x', '--target_x',
                type=float,
                help='X coordinate target',
                required=True
            )
        self.y_initial = self.get_argument(
                '-y', '--target_y',
                type=float,
                help='Y coordinate target',
                required=True
            )
        self.angle_initial = self.get_argument(
                '-a', '--target_angle',
                type=float,
                help='angle target',
                required=True
            )
        self.distance_to_tag = self.get_argument(
                '-dt', '--distance-to-tag',
                type=float,
                help='distance to goal',
                required=False,
                default=0.5
            )
        self.detect_timeout = self.get_argument(
                '-to', '--detect-timeout',
                type=float,
                help='timeout in seconds to detect tags',
                required=False,
                default=5.0
            )   
        self.stop_distance = self.get_argument(
                '-dstop', '--distance-to-stop',
                type=float,
                help='distance from the lidar to the wall to stop',
                required=False,
                default=0.366
            )
        self.max_pos_error = self.get_argument(
                '-me', '--max-pos-error',
                type=float,
                help='max allowed error in position in front of tag on meters',
                required=False,
                default= 0.06
            )
        self.nav_to_tag = self.get_flag_argument(
                '-nt', '--nav-to-tag',
                help='use if you want to navigate to tag before adjusting',
            )
        self.testing = self.get_flag_argument(
                '-test', '--test',
                help='use if you want to navigate to tag before adjusting',
            )


    def enable_odom_camera(self):
        #TODO: Remove when motion commands enable and disable cameras
        os.system(('ros2 service call /gary/cameras/set_gary_camera_status gary_cameras_msgs/srv/SetGaryCameraStatus "{subscriber: nav_app, name: nav_bottom, type: depth, status: true}"'))


    def disable_odom_camera(self):
        #TODO: Remove when motion commands enable and disable cameras
        os.system('ros2 service call /gary/cameras/set_gary_camera_status gary_cameras_msgs/srv/SetGaryCameraStatus "{subscriber: nav_app, name: nav_bottom, type: depth, status: false}"')
    
    
    async def finish_with_error(self, error_message):
        self.log.error(error_message.upper())
        self.finish_app()


    def cb_nav_finish(self, error, error_msg):
        if error != 0:
            self.__navigation_error = [error, error_msg]


    def tags_cb(self, detections, timestamp):
        for detection in list(detections.values()):
            if detection['tag_id'] is self.TAG_IDS[0]:
                if self.__waiting_detection:
                    self.log.info(f'Tag detected')
                    self.__detection_tag_left = detection
                    self.__waiting_detection = False

        
    async def get_goal_to_tag(self, 
                detection, 
                distance_between_tags: 0.20,
                distance_to_tag: float = 0.6
            ):
        quaternion = detection['pose_map'].pose.orientation
        quaternion = [quaternion.x , quaternion.y, quaternion.z, quaternion.w]
        orientation = tf_transformations.euler_from_quaternion(quaternion)
        position = detection['pose_map'].pose.position
        return await self.get_goal_to_position(
                x_coordinate=position.x, 
                y_coordinate=position.y, 
                orientation=orientation[2], 
                horizontal_offset=distance_between_tags/2, 
                distance_to_tag=distance_to_tag,
            )
    
        
    async def get_goal_to_position(self, 
                x_coordinate: float, 
                y_coordinate: float, 
                orientation: float, 
                horizontal_offset: float = 0.20,
                distance_to_tag: float = 0.6
            ):
        tag_map_coordinate = [x_coordinate, y_coordinate]
        goal_coordinate_x = tag_map_coordinate[0] + \
                (distance_to_tag * math.cos(orientation))
        goal_coordinate_y = tag_map_coordinate[1] + \
                (distance_to_tag * math.sin(orientation))
        #move horizontal coordinate                        
        goal_coordinate_x -= (horizontal_offset * math.sin(orientation))
        goal_coordinate_y += (horizontal_offset * math.cos(orientation))
        
        goal_coordinates = [
                goal_coordinate_x, 
                goal_coordinate_y, 
                (orientation - 3.141592)
            ]
        self.log.warn(f'Goal to position calculated...')
        if goal_coordinates[0] == 0.0 or goal_coordinates[1] == 0.0 :
            return
        elif math.isnan(goal_coordinates[0]):
            return None
        elif math.isnan(goal_coordinates[1]):
            return None
        return goal_coordinates
    

    def start_constants(self):
        self.CAMERA = 'nav_bottom'
        self.TAG_SIZE =  self.tags_size
        self.TAG_IDS =  [self.left_id, self.right_id]  
        self.TAG_FAMILY = 'tag36h11'  
        self.DISTANCE_BETWEEN_TAGS = self.dist_betw_tags 
        self.DISTANCE_TO_TAG = 1.2
        self.FINAL_DISTANCE_TO_TAG = self.distance_to_tag 
        self.ERROR_THRESHOLD = self.max_pos_error 
        self.DETECT_TIMEOUT = self.detect_timeout
        self.ANGLE_TO_DETECT_WALL = self.lidar_angle/2 
        self.STOP_DISTANCE = self.stop_distance

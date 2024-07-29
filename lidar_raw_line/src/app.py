import json
import numpy as np
import math


from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.enumerations import ANGLE_UNIT

DEGREE_TO_RADIAN = 0.0174533
DISTANCE_BASE_LINK_TO_FRONT_LIDAR = 0.15
DISTANCE_BASE_LINK_TO_BACK_LIDAR = 0.15

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling lidar controller')
        self.lidar:LidarController = await self.enable_controller('lidar')

        self.log.info('Laser info:')
        self.lidar_info = self.lidar.get_laser_info(ang_unit = ANGLE_UNIT.RADIANS)
        self.log.info(json.dumps(self.lidar_info, indent=2))
        
        self.lower_angle = -DEGREE_TO_RADIAN * self.angle
        self.upper_angle = DEGREE_TO_RADIAN * self.angle
        
        self.lidar_distance = DISTANCE_BASE_LINK_TO_FRONT_LIDAR
        if self.back:
            self.lidar_distance = DISTANCE_BASE_LINK_TO_BACK_LIDAR


    async def loop(self):
        # Get data
        raw_data = self.lidar.get_raw_data()
        
        # if back is enabled, shift the data 180 degrees
        if self.back:
            shift = len(raw_data) // 2
            raw_data = np.roll(raw_data, shift)
        
        self.__angle_min = self.lidar_info['angle_min']
        self.__angle_max = self.lidar_info['angle_max']
        self.__angle_increment = self.lidar_info['angle_increment']
        
        min_index = int(math.ceil( 
                (self.lower_angle - self.__angle_min) / self.__angle_increment 
            ))
        max_index = int(math.floor(
                (self.upper_angle - self.__angle_max) / self.__angle_increment 
            ))

        data = raw_data[min_index:max_index]
        # remove all inf values
        data = [x for x in data if x != float('inf')]
        
        # mean
        mean = np.mean(data)-self.lidar_distance
        self.log.warn(f'Distance to target: {mean} meters')

        await self.sleep(self.period)
        

    async def finish(self):
        self.log.info('App finished')


    def get_arguments(self):
        self.back = self.get_flag_argument(
                '-b', '--back',
                help='Shows the back lidar distance',
            )
        
        self.period = self.get_argument(
                '-p', '--period',
                type=float,
                help='Scanning period',
                default=1.0
            )
        
        self.angle = self.get_argument(
                '-a', '--a',
                type=float,
                help='Angle of detection of the lidar',
                default=1.0
            )

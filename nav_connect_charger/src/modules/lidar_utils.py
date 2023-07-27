import math
import copy
import numpy as np

from raya.enumerations import ANGLE_UNIT, SHAPE_TYPE
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from raya.controllers.base_controller import BaseController
from raya.application_base import RayaApplicationBase
import statistics


class LidarUtils():
    def __init__(self, app: RayaApplicationBase):
        app.log.info('Lidar utils started.')


    async def get_lidar_between(self,
                                lidar_data,
                                lower_angle:float, 
                                upper_angle:float):
        
        lidar_array = copy.copy(lidar_data)
        step_size = 2 * np.pi / len(lidar_array)
        if lower_angle < 0:
            lower_angle = 2 * np.pi + lower_angle 
            upper_angle = 2 * np.pi + upper_angle
        initial_index = math.floor(lower_angle/step_size)
        final_index = math.ceil(upper_angle/step_size)
        lidar_array += lidar_array
        limited_data = lidar_array[initial_index: final_index]
        limited_data = np.flip(limited_data)
        lidar_data = await self.get_normalized_lidar(lower_angle, 
                                    limited_data, step_size)
        return lidar_data


    async def get_normalized_lidar(self, 
                                    initial_angle, 
                                    lidar_data, 
                                    step_size):
        point_angle = initial_angle
        lidar_data_coordinates = []
        angles_array = []
        for i,distance in enumerate(lidar_data):
            coordinate = distance * abs(math.cos(point_angle))
            lidar_data_coordinates.append(coordinate)
            angles_array.append(point_angle)
            point_angle += step_size
        return await self.extrapolate_data(lidar_data_coordinates)

    
    async def extrapolate_data(self, data):
        for i, number in enumerate(data):
            if abs(number) > 100 or number <= 1.0:
                current_index = 0
                while data[i + current_index] <= 1.0 or \
                    abs(data[i + current_index]) > 100:
                        current_index += 1
                        if current_index + i > len(data) - 1:
                            current_index = -1
                            break
                data[i] = data[i + current_index]
        return data
    

    async def get_distance_to_line(self, lidar_data):
        return statistics.mean(lidar_data)
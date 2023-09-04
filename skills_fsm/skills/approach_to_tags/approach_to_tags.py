import math
import queue
import time
import asyncio
import numpy as np
import tf_transformations as tftr
from transforms3d import euler

from raya.controllers import MotionController
from raya.controllers import CVController
from raya.skills import RayaFSMSkill

from .constants import *


class SkillApproachToTags(RayaFSMSkill):

    ### FSM CONSTANTS ###

    # ENABLEEEEEE
    TICK_PERIOD = 0.1

    STATES = [
            'READ_APRILTAG',
            'GO_TO_INTERSECTION',
            'READ_APRILTAG_2',
            'ROTATE_TO_APRILTAGS',
            'STEP_N',
            'READ_APRILTAGS_N',
            'CENTER_TO_TARGET',
            'READ_APRILTAGS_FINAL',
            'MOVE_LINEAR_FINAL',
            'END'
        ]

    INITIAL_STATE = 'READ_APRILTAG'

    END_STATES = [
        'END',
    ]

    STATES_TIMEOUTS = {
        'READ_APRILTAG' :       (NO_TARGET_TIMEOUT_LONG, ERROR_NO_TARGET_FOUND),
        'READ_APRILTAGS_N' :    (NO_TARGET_TIMEOUT_LONG, ERROR_NO_TARGET_FOUND),
        'READ_APRILTAGS_FINAL': (NO_TARGET_TIMEOUT_LONG, ERROR_NO_TARGET_FOUND),
    }

    DEFAULT_SETUP_ARGS = {
        'log_transitions':True,
        'distance_to_goal': 0.5,
        'angle_to_goal': 0.0,
        'intersection_threshold': 0.2,
        'angular_velocity': 10,
        'linear_velocity': 0.1,
        'min_correction_distance': MIN_CORRECTION_DISTANCE,
        'save_trajectory': False,
        'step_size': 0.2,
        'tags_to_average': 6,
        'max_x_error_allowed': 0.02,
        'max_y_error_allowed': 0.05,
        'max_angle_error_allowed': 5.0,
    }

    DEFAULT_EXECUTION_ARGS = {}

    ### SKILL METHODS ###

    async def setup(self):
        self.timer1 = None
        self.step_task = None

        self.motion:MotionController = await self.get_controller('motion')
        self.cv:CVController = await self.enable_controller('cv')
        model_params = {
                'families' : 'tag36h11',
                'nthreads' : 4,
                'quad_decimate' : 2.0,
                'quad_sigma': 0.0,
                'decode_sharpening' : 0.25,
                'refine_edges' : 1,
                'tag_size' : self.setup_args['tags_size'],
            }
        self.predictor = await self.cv.enable_model(
                name='apriltags', 
                source=self.setup_args['working_camera'],
                model_params = model_params
            )


    async def finish(self):
        pass


    ### HELPERS ###


    def setup_variables(self):
        self.handler_names = HANDLER_NAMES
        self.handler_name = type(self.predictor).__name__
        self.approach = self.handler_names[self.handler_name]
        
        #flags
        self.is_there_detection = False
        self.waiting_detection = True
        self.wait_until_complete_queue = True
        self.is_final_step = False

        #calculations
        self.correct_detection = None
        self.angle_intersection_goal = None
        self.angle_robot_intersection = None
        self.angular_sign = None
        self.angle_robot_goal = None
        self.linear_distance = None
        
        self.__predictions_queue= queue.Queue()

        self.additional_distance= self.setup_args['min_correction_distance']

        self.predictor.set_detections_callback(
                callback=self._callback_predictions,
                as_dict=True,
                call_without_detections=True
            )

    def validate_arguments(self):
        self.setup_variables()
        if self.setup_args['angle_to_goal'] > 180.0 \
            or self.setup_args['angle_to_goal'] < -180.0:
            self.abort(*ERROR_INVALID_ANGLE)
        if not self.handler_name in HANDLER_NAMES:
            self.abort(*ERROR_INVALID_PREDICTOR)
        if self.setup_args['identifier'] is None and \
                HANDLER_NAMES[self.handler_name] is not None:
            self.abort(*ERROR_IDENTIFIER_NOT_DEFINED)
        if len(self.setup_args['identifier'])>2:
            self.abort(*ERROR_IDENTIFIER_LENGTH_HAS_BEEN_EXCEED)


    async def rotate_and_move_linear(self):
        self.log.debug(
                f'rotating {self.angular_sign* self.angle_robot_intersection} '
                f'linear {self.linear_distance}'
            )
        if abs(self.projected_error_y) > self.setup_args['max_y_error_allowed']:
            self.log.debug('rotating because projected error exceed limit')
            await self.motion.rotate(
                    angle=abs(self.angle_robot_intersection), 
                    angular_speed=self.setup_args['angular_velocity'] * self.angular_sign, 
                    wait=True,
                )
        await self.motion.move_linear(
                distance=self.linear_distance, 
                x_velocity=self.setup_args['linear_velocity'], 
                wait=True,
            )
    

    def start_detections(self, wait_complete_queue=True):
        self.is_there_detection = False
        self.waiting_detection = True
        self.wait_until_complete_queue = wait_complete_queue
        self.correct_detection = None


    def stop_detections(self):
        self.waiting_detection = False

    
    def check_initial_position(self):
        x_final = False
        y_final = False
        robot_position = [0, 0, 0]
        self.initial_pos = self.correct_detection
        distance_x, distance_y = self.get_relative_coords(
            self.correct_detection[:2], robot_position[:2], 
            self.correct_detection[2])
        distance_x = abs(distance_x - self.setup_args['distance_to_goal'])
        if abs(distance_x) <= X_THRESHOLD_ERROR:
            x_final = True                         
        if abs(distance_y) <= Y_THRESHOLD_ERROR:
            y_final = True
        if x_final == True and y_final == True:  
            return True 
        ini_target_distance = self.get_euclidean_distance(
            robot_position[:2], self.correct_detection)
        if ini_target_distance < (self.setup_args['distance_to_goal'] + 
                                  self.setup_args['min_correction_distance']):
            self.log.debug("ERROR_TOO_CLOSE_TO_TARGET")
            self.abort(
                    ERROR_TOO_CLOSE_TO_TARGET,
                    f'Robot is too close to the target. It is '
                    f'{ini_target_distance:.2f}, and it must be at least the '
                    f'distance to goal ({self.setup_args["distance_to_goal"]:.2f}) '
                    f'+ MIN_CORRECTION_DISTANCE ({MIN_CORRECTION_DISTANCE})'
                )
            

    def planning_calculations(self):
        (self.angular_sign, self.distance, self.distance_to_inter, 
         self.angle_robot_intersection,
         self.angle_intersection_goal) = \
             self.get_intersection_info()
        self.angle_robot_goal = self.get_angle(
                [0,0,0], 
                self.correct_detection
            )
        self.projected_error_y = self.get_error_projection_y()
        
    def get_error_projection_y(self):
        original_translation = (self.correct_detection[0], 
                                self.correct_detection[1], 
                                0.0)
        original_rotation = (0, 0, math.radians(self.correct_detection[2]))  # 45 degrees in radians
        original_matrix = tftr.compose_matrix(translate=original_translation, angles=original_rotation)
        inverse_matrix = tftr.inverse_matrix(original_matrix)
        inverse_translation = tftr.translation_from_matrix(inverse_matrix)
        inverse_rotation = tftr.euler_from_matrix(inverse_matrix)
        
        error_y = inverse_translation[1] + np.sign(inverse_rotation[2]) * \
        np.tan(np.pi-abs(inverse_rotation[2]))*(inverse_translation[0] -
        self.setup_args['distance_to_goal'])
        self.log.debug(f"projected y error {error_y}")
        return error_y

    def get_intersection_info(self):
        line_2 = self.__get_proyected_point(
            self.correct_detection[0], self.correct_detection[1], 
            self.correct_detection[2], 
            self.setup_args['distance_to_goal']+self.additional_distance)
        robot_point= [0,0,0]
        p1 = np.array(self.correct_detection[:2])
        p2 = np.array(line_2)
        p0 = np.array(robot_point[:2])
        before = False
    
        left_side = -1
        line_direction = p2 - p1
        intersection = p2
        if intersection[1] > 0:
            left_side = 1
        intersection_direction = np.dot(line_direction, intersection - p0)
        if intersection_direction >= 0:
            before = True
        distance_intersection = self.get_euclidean_distance(intersection, p0)
        min_distance_intersection = self.get_distance_intersection(
                    self.correct_detection[:2], intersection)
        angle_robot_intersection = np.arccos(
            np.dot(np.array([1,0]),(p2-p0)/np.linalg.norm(p2-p0)))

        angle_intersection_goal = -np.sign(min_distance_intersection)*\
            (np.pi-abs(np.arccos(np.dot((p1-p2)/np.linalg.norm(p1-p2),
                                        (p0-p2)/np.linalg.norm(p0-p2)))))
        
        
        return ( left_side, 
                distance_intersection, abs(min_distance_intersection), 
                math.degrees(angle_robot_intersection),
                math.degrees(angle_intersection_goal))
    
    
    def _callback_predictions(self, predictions, timestamp):
        if predictions:
            __predictions = predictions
            __predictions['timestamp'] = timestamp[0]+timestamp[1]/1e9
            if self.waiting_detection:
                self.__predictions_queue.put(predictions)
                if self.__predictions_queue._qsize() == \
                        self.setup_args['tags_to_average'] or \
                        not self.wait_until_complete_queue:                
                    self.__update_predictions()
                

    def __update_predictions(self ):
        predicts = []
        temporal_queue = queue.Queue()
        
        while not self.__predictions_queue.empty():
            prediction = self.__predictions_queue.get()
            goal =self.__proccess_prediction(prediction)
            if not goal:
                continue
            temporal_queue.put(prediction)
            predicts.append(goal)
        self.robot_position=()

        if (len(predicts) == self.setup_args['tags_to_average'] or 
            not self.wait_until_complete_queue):
            correct_detection=self.__process_multiple_detections(predicts)
            if correct_detection:
                self.correct_detection = correct_detection
                self.is_there_detection = True
                self.waiting_detection = False
                return
            else:
                temporal_queue.get() # discarding last value 

        while not temporal_queue.empty():
            self.__predictions_queue.put(temporal_queue.get())


    def __proccess_prediction(self, prediction):
        predicts=[]
        list_size = len(self.setup_args['identifier']) 
        ids = [int(id) for id in self.setup_args['identifier']]
        for pred in prediction.values():
            if type(pred) == float:
                continue
            if int(pred[self.approach]) not in ids:
                continue
            predicts.append(pred)
        if len(predicts) < list_size:
            return None
        predicts_final=[]
        for pred in predicts:
            if pred['pose_base_link']:
                angle=self.__quaternion_to_euler(pred['pose_base_link'])[2]
                goal = [pred['pose_base_link'].pose.position.x,
                                pred['pose_base_link'].pose.position.y,
                                angle+
                                self.setup_args['angle_to_goal']]
                if list_size == 1:
                    return goal
                predicts_final.append((goal, goal[2]))
            
        goal = self.__process_multiple_tags(predicts_final)       
        return goal 


    def __process_multiple_detections(self, predictions):
        # Step 1: Calculate the mean of the list of predictions (arrays of three values)
        predictions_np = np.array(predictions)
        valid_predictions = predictions_np[~np.isnan(
            predictions_np).any(axis=1)]

        if len(valid_predictions) == 0:
            return None  # Return None if all positions have NaN values

        # Step 2: Calculate the mean of the valid predictions (arrays of three values)
        mean_prediction = np.mean(valid_predictions, axis=0)

        # Step 3: Get the values below the mean
        below_mean_values = valid_predictions[
            (abs(valid_predictions-mean_prediction)<=0.3).sum(axis=1)>1, :]
        below_mean_values = below_mean_values[
            (abs(below_mean_values[:,-1]-mean_prediction[-1])<=10), :]
        if len(below_mean_values) == 0:
            return None
        # Step 5: Calculate the mean of the values below the mean
        mean_below_mean = np.mean(below_mean_values, axis=0)

        return mean_below_mean.tolist()
    

    def __process_multiple_tags(self, predicts):
        pt1 = predicts[0][0]
        pt2 = predicts[1][0]
        angle4 = math.degrees(np.arctan((pt1[1] - pt2[1])/(pt1[0] - pt2[0])))
        angle5 = np.sign(angle4)*(90-abs(angle4))
        final_point = ((pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2, 
                       np.sign(angle5)*(180-abs(angle5))+
                                self.setup_args['angle_to_goal'])
        return final_point  
    

    def __get_proyected_point(self, x, y, angle, distance):
        angulo_rad = math.radians(angle)
        x_final = x + distance * math.cos(angulo_rad)
        y_final = y + distance * math.sin(angulo_rad)
        return (x_final, y_final)


    def get_relative_coords(self, punto_a, punto_b, angulo_direccion):
        x_a, y_a = punto_a
        x_b, y_b = punto_b
        delta_x = x_b - x_a
        delta_y = y_b - y_a
        angulo_rad = math.radians(angulo_direccion)
        x_rel = delta_x * math.cos(angulo_rad) + delta_y * math.sin(angulo_rad)
        y_rel = delta_y * math.cos(angulo_rad) - delta_x * math.sin(angulo_rad)
        return x_rel, y_rel


    def get_euclidean_distance(self, pt1, pt2):
        distance = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
        return distance
    

    def __quaternion_to_euler(self, point_pose):
        x = point_pose.pose.orientation.x
        y = point_pose.pose.orientation.y
        z = point_pose.pose.orientation.z
        w = point_pose.pose.orientation.w
        quat = [w, x, y, z]
        euler_angles = euler.quat2euler(quat, 'sxyz')
        roll = math.degrees(euler_angles[0])
        pitch = math.degrees(euler_angles[1])
        yaw = math.degrees(euler_angles[2])

        return roll, pitch, yaw
    
    def get_distance_intersection(self,punto1, punto2):
        m = (punto2[1] - punto1[1]) / (punto2[0] - punto1[0])
        b = punto1[1] - m * punto1[0]
        return b

    def get_angle(self, robot_point, line_point1):
        robot_angle_rad = np.radians(robot_point[2])
        robot_direction = np.array([np.cos(robot_angle_rad), 
                                    np.sin(robot_angle_rad)])
        line_direction = np.array(line_point1[:2]) - np.array(robot_point[:2])
        line_direction /= np.linalg.norm(line_direction)  # Normalizar el vector de dirección de la línea
        angle_rad = np.arctan2(line_direction[1], 
                               line_direction[0]) - np.arctan2(
            robot_direction[1], robot_direction[0])
        angle_deg = np.degrees(angle_rad)

        return angle_deg
    
    def motion_running(self):
        return self.motion.is_moving()


    ### ACTIONS ###


    async def enter_READ_APRILTAG(self):
        self.validate_arguments()
        self.start_detections()


    async def enter_GO_TO_INTERSECTION(self):
        self.planning_calculations()
        self.linear_distance= self.distance
        if abs(self.distance_to_inter) > MAX_MISALIGNMENT:
            self.abort(
                    ERROR_TOO_DISALIGNED,
                    'The robot is disaligned by '
                    f'{abs(self.distance_to_inter)} meters, max '
                    f'{MAX_MISALIGNMENT} is allowed.'
                )
        self.step_task = asyncio.create_task(self.rotate_and_move_linear())


    async def enter_READ_APRILTAG_2(self):
        self.start_detections(wait_complete_queue=False)
        self.timer1 = time.time()
        

    async def enter_ROTATE_TO_APRILTAGS(self):
        self.log.debug(f'rotating {self.angle_intersection_goal}')
        ang_vel=(self.setup_args['angular_velocity'] *
                 np.sign(self.angle_intersection_goal))
        await self.motion.rotate(
                angle=abs(self.angle_intersection_goal), 
                angular_speed=ang_vel, 
                wait=False
            )

    
    async def  enter_READ_APRILTAGS_N(self):
        self.start_detections()
        

    async def enter_STEP_N(self):
        self.additional_distance = 0.0
        self.planning_calculations()
        self.linear_distance = self.setup_args['step_size']
        if self.distance<=self.setup_args['step_size']:
            self.is_final_step=True
            self.linear_distance=self.distance
        self.log.debug(f"distance: {self.distance} ")
        self.step_task = asyncio.create_task(self.rotate_and_move_linear())


    async def enter_CENTER_TO_TARGET(self):
        self.planning_calculations()
        if abs(self.angle_robot_goal) > \
            self.setup_args['max_angle_error_allowed']:
            ang_vel=(self.setup_args['angular_velocity'] *
                    np.sign(self.angle_robot_goal))
            await self.motion.rotate(
                    angle=abs(self.angle_robot_goal), 
                    angular_speed=ang_vel, 
                    wait=False
                )
    

    async def enter_READ_APRILTAGS_FINAL(self):
        self.start_detections()
        
    
    async def enter_MOVE_LINEAR_FINAL(self):
        self.planning_calculations()
        distance_x, distance_y = self.get_relative_coords(
            self.correct_detection[:2], [0,0], 
            self.correct_detection[2])
        linear_distance = distance_x - self.setup_args['distance_to_goal']
        self.log.debug(f"linear distance to correct {linear_distance}"
                           f" error y {distance_y} angle_tag "
                           f"{self.correct_detection[2]}")
        if abs(linear_distance) > self.setup_args['max_x_error_allowed']:
            await self.motion.move_linear(distance=abs(linear_distance), 
                                            x_velocity=(
            self.setup_args['linear_velocity']*np.sign(linear_distance)), 
                                            wait=False)


    ### TRANSITIONS ###


    async def transition_from_READ_APRILTAG(self):
        if self.is_there_detection:
            if self.check_initial_position():
                self.set_state('CENTER_TO_TARGET')
            else:
                self.set_state('GO_TO_INTERSECTION')


    async def transition_from_GO_TO_INTERSECTION(self):
        if self.step_task.done():
            await self.step_task
            self.set_state('READ_APRILTAG_2')


    async def transition_from_READ_APRILTAG_2(self):
        if (time.time()-self.timer1) > NO_TARGET_TIMEOUT_SHORT:
            self.stop_detections()
            if self.is_there_detection:
                self.set_state('READ_APRILTAGS_N')
            else:
                self.set_state('ROTATE_TO_APRILTAGS')


    async def transition_from_ROTATE_TO_APRILTAGS(self):
        if not self.motion_running():
            self.motion.check_last_motion_exception()
            self.set_state('READ_APRILTAGS_N')
    

    async def transition_from_STEP_N(self):
        if self.step_task.done():
            await self.step_task
            self.set_state('READ_APRILTAGS_N')


    async def transition_from_READ_APRILTAGS_N(self):
        if self.is_there_detection:
            if self.is_final_step:
                self.set_state('CENTER_TO_TARGET')
            else:
                self.set_state('STEP_N')
                

    async def transition_from_CENTER_TO_TARGET(self):
        if not self.motion_running():
            self.motion.check_last_motion_exception()
            self.set_state('READ_APRILTAGS_FINAL')

    
    async def transition_from_READ_APRILTAGS_FINAL(self):
        if self.is_there_detection:
            self.set_state('MOVE_LINEAR_FINAL')


    async def transition_from_MOVE_LINEAR_FINAL(self):
        if not self.motion_running():
            self.motion.check_last_motion_exception()
            self.set_state('END')

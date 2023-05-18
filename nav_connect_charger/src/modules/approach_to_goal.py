import time
import math
import rclpy
import numpy as np
import rclpy.qos as qos
import tf_transformations
from tf2_ros.buffer import Buffer
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TransformStamped
from rclpy.callback_groups import ReentrantCallbackGroup

from raya.exceptions import RayaException
from raya.handlers.cv.tags_detector_handler import TagsDetectorHandler


class ApproachToGoal:
    def __init__(self,
                app,
                id_tag1: int, 
                id_tag2: int, 
                distance_to_tag: float, 
                error_threshold: float,
                detector: TagsDetectorHandler
            ):

        self.tags_ids = [id_tag1, id_tag2]
        self.distance_to_tag = distance_to_tag
        self.error_threshold = error_threshold
        self.detector = detector
        self.app = app
        interface = self.app._RayaApplicationBase__raya_interf
        self.__node = interface._RayaInterface__node
        self.__ros_init()


    def enable(self):
        self.__pub_cmdvel = self.__node.create_publisher(
                msg_type=Twist, 
                topic='/cmd_vel',
                qos_profile=self.__qos_default,
                callback_group=self.__callback_group
            )
        self.detector.set_detections_callback(
            callback=self.__tags_cb,
            as_dict=True,
            call_without_detections=True,
        )
        self.VEL_MAX = 0.09
        self.CORRECTION_ANGULAR = 0.1
        self.tf_buffer = Buffer()
        self.angular = 0.0
        self.linear = self.VEL_MAX
        self.x = self.distance_to_tag
        self.I = 0.0
        self.e_prev = 0.0
        self.t_prev = time.time()

        self.x_act = {self.tags_ids[0]: 1, self.tags_ids[1]: 1}
        self.y_act = {self.tags_ids[0]: 1, self.tags_ids[1]: 1}
        self.found = {self.tags_ids[0]: False, self.tags_ids[1]: False}
        self.counter = {self.tags_ids[0]: 0, self.tags_ids[1]: 0}
        self.stage=1
        self.done = False
        self.move_backward = False

    
    def disable(self):
        #TODO: Remove callback and publisher
        pass


    async def approach_between_tags(self):
        try: #TODO: Remove try when task allow exception handling
            while not self.done: 
                if self.stage == 1:
                    pid_response = await self.__pid(
                            Kp=0.30, 
                            Ki=0.20, 
                            Kd=0.1, 
                            error=self.error_threshold
                        )
                    if await pid_response:
                        self.stage = 2
                if self.stage == 2:
                    self.linear=0.0
                    self.VEL_MAX=0.0
                    pid_response = self.__pid(
                            Kp=0.4, 
                            Ki=0.25, 
                            Kd=0.1, 
                            error=self.error_threshold, 
                            error_orientation=True
                        )
                    if await pid_response:
                        self.done = True
                        return True
                await self.app.sleep(0.1)
        except Exception as e:
            print('error on approach to tag = ', e)


    def __ros_init(self):
        self.__callback_group = ReentrantCallbackGroup()
        self.__qos_default = qos.qos_profile_system_default

    
    def __tags_cb(self, detections, timestamp):
        for detection in list(detections.values()):
            if detection['tag_id'] in self.tags_ids:
                position = detection['pose_base_link'].pose.position
                self.x_act[detection['tag_id']] = position.x
                self.y_act[detection['tag_id']] = position.y
                self.found[detection['tag_id']] = True

    
    async def __pid(self, 
                Kp, 
                Ki=0.0, 
                Kd=0.0, 
                error=0.06, 
                error_orientation=False
            ):
        try:
            e, angle = await self.__get_error(error_orientation)
            if abs(e) < error:
                self.VEL_MAX = 0.0
                self.CORRECTION_ANGULAR = 0.05
                return True
            t = time.time()
            P = Kp*angle
            self.I = self.I + Ki*angle*(t - self.t_prev)
            D = Kd*(angle - self.e_prev)/(t - self.t_prev)
            value = P + self.I + D
            if not error_orientation and abs(value) >0.015:
                self.angular = value
            else: 
                self.angular = 0.015 * abs(value)/value
            self.e_prev = angle
            self.t_prev = t
            await self.__update_cmd_vel(self.linear, self.angular)
        except RayaException as e:
            print('not found tag')
            self.t_prev = time.time()
            self.I = self.I*0.9
            self.e_prev = self.e_prev*0.9
        except ValueError as e:
            print('nan value ')
        return False
    

    async def __update_cmd_vel(self, linear_speed, angular_speed):
        cmdvel = Twist()
        cmdvel.linear.x = linear_speed
        cmdvel.angular.z = angular_speed
        self.__pub_cmdvel.publish(cmdvel)

    
    async def __get_error(self, error_orientation=False):
        if not self.move_backward:
            if not self.found[self.tags_ids[1]] and \
                    not self.found[self.tags_ids[0]]:
                raise RayaException(f'Could not find detection of  tag')
            elif not self.found[self.tags_ids[0]] and \
                    self.found[self.tags_ids[1]]:
                self.counter[self.tags_ids[0]]+=1
                if self.counter[self.tags_ids[0]]>2:
                    await self.__update_cmd_vel(
                            self.VEL_MAX/10, 
                            self.CORRECTION_ANGULAR
                        )
                else:
                    await self.__update_cmd_vel(self.linear, self.angular)
                raise RayaException(f'Could not find detection of  tag')
            elif not self.found[self.tags_ids[1]] and \
                    self.found[self.tags_ids[0]]:
                self.counter[self.tags_ids[1]]+=1
                if self.counter[self.tags_ids[1]]>2:
                    await self.__update_cmd_vel(
                            self.VEL_MAX/10, 
                            -self.CORRECTION_ANGULAR
                        )
                else:
                    await self.__update_cmd_vel(self.linear, self.angular)
                raise RayaException(f'Could not find detection of  tag')
        

        self.counter = {self.tags_ids[0]: 0, self.tags_ids[1]: 0}
        self.found = {self.tags_ids[0]: False, self.tags_ids[1]: False}

        self.orientation = -np.pi - \
            np.arctan(
                    (
                        self.x_act[self.tags_ids[1]]- \
                        self.x_act[self.tags_ids[0]]) /
                    (
                        self.y_act[self.tags_ids[1]]- \
                        self.y_act[self.tags_ids[0]]
                    )
                )

        if np.isnan(self.orientation):
            raise ValueError('error in pose from base link to tags')

        q = tf_transformations.quaternion_from_euler(0, 0, self.orientation)
        transform0 = TransformStamped()
        transform0.child_frame_id = 'tag_0'
        transform0.header.frame_id = 'base_link'
        transform0.header.stamp = self.__node.get_clock().now().to_msg()
        transform0.transform.translation.x = self.x_act[self.tags_ids[0]]
        transform0.transform.translation.y = self.y_act[self.tags_ids[0]]
        transform0.transform.rotation.x = q[0]
        transform0.transform.rotation.y = q[1]
        transform0.transform.rotation.z = q[2]
        transform0.transform.rotation.w = q[3]
        self.tf_buffer.set_transform_static(
            transform=transform0, authority='test')
        transform1 = TransformStamped()
        transform1.child_frame_id = 'tag_1'
        transform1.header.frame_id = 'base_link'
        transform0.header.stamp = self.__node.get_clock().now().to_msg()
        transform1.transform.translation.x = self.x_act[self.tags_ids[1]]
        transform1.transform.translation.y = self.y_act[self.tags_ids[1]]
        transform1.transform.rotation.x = q[0]
        transform1.transform.rotation.y = q[1]
        transform1.transform.rotation.z = q[2]
        transform1.transform.rotation.w = q[3]
        self.tf_buffer.set_transform_static(
            transform=transform1, authority='test')

        trans0 = self.tf_buffer.lookup_transform(
            'tag_0', 'base_link', rclpy.time.Time())
        trans1 = self.tf_buffer.lookup_transform(
            'tag_1', 'base_link', rclpy.time.Time())
        error_x = self.x-(
                trans0.transform.translation.x +
                trans1.transform.translation.x
            )/2
        error_y = -trans0.transform.translation.y - \
                trans1.transform.translation.y
        
        #print(f' error_x: {error_x} error_y {error_y}')
        angle_d = np.arctan2(-1.2*error_x, -error_y)
        angle_a = tf_transformations.euler_from_quaternion([
                trans0.transform.rotation.x,
                trans0.transform.rotation.y,
                trans0.transform.rotation.z,
                trans0.transform.rotation.w
            ])[2]+np.pi
        angle_a = tf_transformations.euler_from_quaternion(
                tf_transformations.quaternion_from_euler(0, 0, angle_a)
            )[2]
        angle_d = tf_transformations.euler_from_quaternion(
                tf_transformations.quaternion_from_euler(0, 0, np.pi/2-angle_d)
            )[2]

        value = math.sqrt(error_x**2+2*error_y**2)
        angle = angle_d-angle_a
        if error_orientation:
            return angle_a, -angle_a

        if error_x > -0.3:
            self.linear = self.VEL_MAX/2.5
            angle=angle*0.03
        if error_x > -0.12:
            self.linear = self.VEL_MAX/5
            angle=angle*0.01
        if error_x > 0.0 and abs(error_y) > 0.06:
            self.move_backward = True
        if abs(error_y) < 0.02:
            self.linear = -error_x*0.3
            self.move_backward = False
            angle = -angle_a
        if self.move_backward:
            self.linear = -0.04
            angle = 0.0
            if error_x < -0.4:
                self.move_backward = False
                self.linear = self.VEL_MAX
        return value, angle

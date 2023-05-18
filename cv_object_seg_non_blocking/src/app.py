# System Imports
import json
import cv2
import collections
import numpy as np

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Segmentation Example')

        self.last_segmentations = None
        self.last_segmentations_timestamp = None
        self.last_color_frames = collections.deque(maxlen=60)

        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

        # If a camera name was set
        if self.camera != None:
            cams = set(self.available_cameras)
            if self.camera in cams:
                self.working_camera = self.camera
            else:
                self.log.info('Camera name not available')
                self.finish_app()
                return
        else:
            # If a camera name wasn't set it works with camera in zero position
            self.working_camera = self.available_cameras[0]

        # Enable camera
        await self.cameras.enable_color_camera(self.working_camera)

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        # Enable segmentator
        self.log.info('Enabling model...')
        self.segmentator = await self.cv.enable_model(
                name=str(self.model),
                source=str(self.working_camera)
            )
        self.log.info('Model enabled')
        self.log.info(f'Objects names: {self.segmentator.get_objects_names()}')

        # Create listeners
        self.cameras.create_color_frame_listener(
                camera_name=self.working_camera,
                callback=self.callback_color_frame
            )
        self.segmentator.set_segmentations_callback(
                callback=self.callback_all_objects,
                as_dict=True,
                call_without_segmentations=True,
            )
        self.time_counter = 0


    async def loop(self):
        self.log.info('Doing other (non blocking) stuff')
        await self.sleep(1.0)
        self.time_counter += 1
        if self.time_counter>self.duration:
            self.finish_app()
            
        
    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model_obj=self.segmentator)
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='yolov8s_seg_coco',
                help='face model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )
        self.callback_object = self.get_argument(
                '-co', '--callback-object', 
                default=['book'],
                nargs='+', 
                type=list,
                help=(
                        'list of strings with the objects to detect'
                        'in not blockin mode'
                    )
            )
        self.duration = self.get_argument(
                '-d',  '--duration', 
                type=float, 
                default=20.0,
                help='model running duration'
            )
        

    async def callback_specific_obj(self,
                segmentated_obj, 
                obj_info,
                timestamp
            ):
        self.log.info(f'!!!!')
        self.log.info(f'Object {segmentated_obj} segmentated')
        self.log.info(f'Object info type: {type(obj_info)}')
        self.log.info(f'Object timestamp {timestamp}')
        self.log.info(f'!!!!')


    def callback_all_objects(self, segmentations, timestamp):
        self.last_segmentations = list(segmentations.values())
        self.last_segmentations_timestamp = timestamp
        self.match_image_segmentations()


    def callback_color_frame(self, image,  timestamp):
        self.last_color_frames.append( (timestamp, image) )
        self.match_image_segmentations()


    def match_image_segmentations(self):
        if self.last_segmentations_timestamp is None or \
                not self.last_color_frames:
            return
        image = None
        for color_frame in self.last_color_frames:
            if color_frame[0] == self.last_segmentations_timestamp:
                image = color_frame[1].copy()
        if image is None:
            return
        segmentation_names = []
        for segmentation in self.last_segmentations:
            contours = np.array(segmentation['contours'], 
                                dtype=np.int32).reshape((-1, 2))
            back = image.copy()
            color = (hash(segmentation['object_name']) % 255, 
                     hash(segmentation['object_name']) % 255, 
                     hash(segmentation['object_name']) % 255)
            cv2.drawContours(
                    image=back, 
                    contours=[contours], 
                    contourIdx=0, 
                    color=color, 
                    thickness=-1
                )
            cv2.drawContours(
                    image=back, 
                    contours=[contours], 
                    contourIdx=0, 
                    color=(0,255,0), 
                    thickness=0, 
                    lineType=cv2.LINE_AA
                )
            alpha = 0.5
            image = cv2.addWeighted(
                    src1=image, 
                    alpha=1-alpha, 
                    src2=back, 
                    beta=alpha, 
                    gamma=0
                )
            image = cv2.putText(
                    img = image, 
                    text = f'{segmentation["object_name"]}'
                           f' {round(segmentation["confidence"], 2)}', 
                    org = (segmentation['bbox'][0], 
                           segmentation['bbox'][1] - 5), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
			        fontScale = 0.5, 
                    color = (0, 0, 255), 
                    thickness = 2)
            segmentation_names.append(segmentation['object_name'])
        show_image(img=image, title='Video from Gary\'s camera')

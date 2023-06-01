# System Imports
import json
import cv2
import collections

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Detection Example')

        self.last_detections = None
        self.last_detections_timestamp = None
        self.last_color_frames = collections.deque(maxlen=60)

        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # If a camera name was set
        if self.camera != None:
            cams = set(self.available_cameras)
            if self.camera in cams:
                self.working_camera = self.camera
            else:
                self.log.error('Camera name not available')
                self.finish_app()
        else:
            # If a camera name wasn't set it works with camera in zero position
            self.working_camera = self.available_cameras[0]

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        # Enable detector
        self.log.info('Enabling model...')
        self.detector = await self.cv.enable_model(
                name=str(self.model),
                source=str(self.working_camera),
                model_params = {'depth': True}
            )
        self.log.info('Model enabled')
        self.log.info(f'Objects labels: {self.detector.get_objects_names()}')

        self.detector.set_img_detections_callback(
                callback=self.callback_all_objects,
                as_dict=True,
                call_without_detections=True,
                cameras_controller=self.cameras
            )
        await self.detector.find_objects(
                objects=self.callback_object, 
                callback_async = self.callback_specific_obj,
                wait=False, 
                timeout=self.duration
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
        await self.cv.disable_model(model_obj=self.detector)
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='yolov5s_coco',
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
                type=list,
                nargs='+', 
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


    async def callback_specific_obj(self,detected_obj, obj_info, timestamp):
        self.log.info(f'!!!!')
        self.log.info(f'Object {detected_obj} detected')
        self.log.info(f'Object info type: {type(obj_info)}')
        self.log.info(f'Object timestamp {timestamp}')
        self.log.info(f'!!!!')


    def callback_all_objects(self, detections, image):
        if image is None:
            return
        show_image(img=image, title='Video from Gary\'s camera')

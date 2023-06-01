# System Imports
import json
import cv2
import collections
import numpy as np

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
                                                   
from raya.tools.image import show_image, draw_on_image, match_image_predictions


class RayaApplication(RayaApplicationBase):
    
    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision hand estimation Example')
        self.i = 0
        self.last_estimations = None
        self.last_estimations_timestamp = None
        self.last_color_frames = collections.deque(maxlen=10)

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

        # Enable estimator
        self.log.info('Enabling model...')
        self.estimator = await self.cv.enable_model(
                name=self.model,
                source=self.working_camera
            )
        self.log.info('Model enabled')

        # Create listener
        self.cameras.create_color_frame_listener(
                camera_name=self.working_camera,
                callback=self.callback_color_frame
            )
        self.estimator.set_estimations_callback(
                callback=self.callback_all_hands,
                as_dict=True,
                call_without_estimations=True,
            )


    async def loop(self):
        await self.sleep(1.0)
        if self.i > 50:
            self.finish_app()
        self.i += 1
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model='estimator', type='hand_pose')
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='mp_hand_pose',
                help='face model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )


    def callback_all_hands(self, estimations, timestamp):
        self.last_estimations = list(estimations.values())
        self.last_estimations_timestamp = timestamp
        self.match_estimations()


    def callback_color_frame(self, image, timestamp):
        self.last_color_frames.append( (timestamp, image) )
        self.match_estimations()


    def match_estimations(self):
        image = match_image_predictions(
                self.last_estimations_timestamp, 
                self.last_color_frames
            )
        if image is None or self.last_estimations is None:
            return
        if self.last_estimations == []:
            show_image(img=image, title='Video from Gary\'s camera')
        else:
            # Draw results on the input image
            img, view_3d = draw_on_image(
                    image=image, 
                    last_predictions=self.last_estimations
                )
            show_image(img=img, title='Video from Gary\'s camera')
            show_image(img=view_3d, title='view_3d from Gary\'s camera')

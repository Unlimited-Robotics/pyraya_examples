# System Imports
import json
import cv2
import collections

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image_once


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info((
                'Ra-Ya Py - Computer Vision - '
                'Face detector one time Example'
            ))
        self.i = 0
        self.last_detections = None
        self.last_detections_timestamp = None
        self.last_color_frames = collections.deque(maxlen=100)
        
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

        # Enable detector
        self.log.info('Enabling model...')
        self.detector = await self.cv.enable_model(
                name=self.model,
                continues_msg=False,
                source=self.working_camera,
            )
        self.log.info('Model enabled')
        # Create listeners
        self.cameras.create_color_frame_listener(
                camera_name=self.working_camera,
                callback=self.callback_color_frame
            )

         
    async def loop(self):
        await self.sleep(1.0)
        self.last_detections, self.last_detections_timestamp = \
                await self.detector.get_detections_once(get_timestamp=True)
        self.match_image_detections()
        if self.i > 50:
            self.finish_app()
        self.i += 1
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model_obj=self.detector)
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='cnn_face',
                help='face model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )


    def callback_color_frame(self, image, timestamp):
        self.last_color_frames.append((timestamp, image))


    def match_image_detections(self):
        if self.last_detections_timestamp is None or \
                not self.last_color_frames:
            return
        image = None
        for color_frame in self.last_color_frames:
            if color_frame[0] == self.last_detections_timestamp:
                image = color_frame[1].copy()
        if image is None:
            return
        for detection in self.last_detections:
            image = cv2.rectangle(
                    img=image, 
                    pt1=(detection['x_min'], detection['y_min']), 
                    pt2=(detection['x_max'], detection['y_max']), 
                    color=(0, 255, 0),
                    thickness=2
                )    
        show_image_once(img=image, title='Video from Gary\'s camera')
        
# System Imports
import json
import collections

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image_once, match_image_predictions, \
                             draw_on_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info((
                'Ra-Ya Py - Computer Vision - Recognizer one time Example'
            ))
        self.i = 0
        self.last_recognitions = None
        self.last_recognitions_timestamp = None
        self.last_color_frames = collections.deque(maxlen=100)

        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

        cams = set(self.available_cameras)
        if self.camera in cams:
            self.working_camera = self.camera
        else:
            self.log.info('Camera name not available')
            self.finish_app()
            return

        # Enable camera
        await self.cameras.enable_camera(self.working_camera)

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        # Enable recognizer
        self.log.info('Enabling model...')
        self.recognizer = await self.cv.enable_model(
                name=self.model,
                continues_msg=False,
                source=self.working_camera
            )
        self.log.info('Model enabled')
        # Create listeners
        self.cameras.create_frame_listener(
                camera_name=self.working_camera,
                callback=self.callback_color_frame
            )       


    async def loop(self):
        await self.sleep(1.0)
        self.last_recognitions, self.last_recognitions_timestamp = \
                await self.recognizer.get_recognitions_once(get_timestamp=True)
        self.process_img()
        if self.i > 50: self.finish_app()
        self.i += 1
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model_obj=self.recognizer)
        self.log.info('Disabling camera...')
        await self.cameras.disable_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='deepknn_face',
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


    def process_img(self):
        image = match_image_predictions(
                    self.last_recognitions_timestamp, 
                    self.last_color_frames
                )
        if image is None:
            return
        if self.last_recognitions:
            image = draw_on_image(
                    image=image, 
                    last_predictions=self.last_recognitions
                )
        show_image_once(img=image, title='Video from Gary\'s camera')     
        
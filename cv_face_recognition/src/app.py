# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image, draw_on_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Face Recognition Example')
        self.i = 0
        
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
        
        # Enable recognizer
        self.log.info('Enabling model...')
        self.recognizer = await self.cv.enable_model(
                name=self.model,
                source=self.working_camera
            )
        self.log.info('Model enabled')

        self.log.info(f'Faces availables: ' \
                      f' {self.recognizer.get_recognitions_names()}')

        # Create listener
        self.recognizer.set_img_recognitions_callback(
                callback=self.callback_all_faces,
                as_dict=True,
                call_without_recognitions=True,
                cameras_controller=self.cameras
            )


    async def loop(self):
        await self.sleep(1.0)
        if self.i > 50:
            self.finish_app()
        self.i += 1
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model='recognizer', type='face')
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.working_camera)
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
        

    def callback_all_faces(self, recognitions, image):
        if recognitions:
            image = draw_on_image(image=image, last_predictions=recognitions)
        show_image(img=image, title='Video from Gary\'s camera')
        
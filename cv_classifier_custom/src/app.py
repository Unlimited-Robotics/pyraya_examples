# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image, draw_on_image
from raya.tools.filesystem import download_file, check_folder_exists


DEFAULT_MODEL_URL = (
        'https://storage.googleapis.com/raya_files/Common/cv_models/' 
        'ur_empty_table_v2.tar.gz'
    )


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision - Classification Example')
        
        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller(ctlr_name='cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'{self.available_cameras}')

        cams = set(self.available_cameras)
        if self.camera in cams:
            self.working_camera = self.camera
        else:
            self.log.info('Camera name not available')
            self.finish_app()
            return

        # Enable camera
        await self.cameras.enable_color_camera(camera_name=self.working_camera)

        # Computer Vision
        self.cv: CVController = await self.enable_controller(ctlr_name='cv')
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        #Check if model exists in data folder, if not download it
        folder_path = f'dat:models/{self.model}'
        if not check_folder_exists(path=folder_path):
            self.log.info('Downloading model folder...')
            download_file(
                    url=DEFAULT_MODEL_URL,
                    folder_path='dat:models/', 
                    extract=True
                )
        # Enable classifier
        self.log.info('Enabling model...')
        self.classifier = await self.cv.enable_model(
                custom_model_path=folder_path,
                continues_msg=False,
                source=self.working_camera
            )
        self.log.info('Model enabled')
        # Create listeners
        self.classifier.set_img_classifications_callback(
                callback=self.callback_all_predictions,
                as_dict=True,
                call_without_classifications=True,
                cameras_controller=self.cameras
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
        await self.cv.disable_model(model_obj=self.classifier)
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(
                camera_name=self.working_camera,
            )
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='ur_empty_table_v2',
                help='classificator model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )
        self.duration = self.get_argument(
                '-d',  '--duration', 
                type=float, 
                default=20.0,
                help='model running duration'
            )
                

    def callback_all_predictions(self, classifications, image):
        if classifications:
            image = draw_on_image(
                    image=image, 
                    last_predictions=classifications
                )
        show_image(img=image, title='Video from Gary\'s camera')

# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image, draw_on_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Segmentation Example')

        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
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
        self.segmentator.set_img_segmentations_callback(
                callback=self.callback_all_predictions,
                as_dict=True,
                call_without_segmentations=True,
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


    def callback_all_predictions(self, segmentations, image):
        if segmentations:
            image = draw_on_image(
                    image=image, 
                    last_predictions=segmentations
                )
        show_image(img=image, title='Video from Gary\'s camera')
        
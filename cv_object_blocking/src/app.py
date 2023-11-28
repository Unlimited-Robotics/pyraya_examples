# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.tools.image import show_image, draw_on_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Detection Example')

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

        # Enable detector
        self.log.info('Enabling model...')
        self.detector = await self.cv.enable_model(
                name=str(self.model),
                source=str(self.working_camera),
                model_params = {'depth': False}
            )
        self.log.info('Model enabled')
        self.log.info(f'Objects labels: {self.detector.get_objects_names()}')

        # Create listeners
        self.detector.set_img_detections_callback(
                callback=self.callback_all_objects,
                as_dict=True,
                call_without_detections=True,
                cameras_controller=self.cameras
            )


    async def loop(self):
        resp = await self.detector.find_objects(
                objects=self.finish_object, 
                wait=True, 
                timeout=self.duration
            )
        if not resp:
            self.log.info(f'Timer Finish!')
        else:
            self.log.info(f'Done!')
        self.finish_app()           
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model_obj=self.detector)
        self.log.info('Disabling camera...')
        await self.cameras.disable_camera(self.working_camera)
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
        self.finish_object = self.get_argument(
                '-f', '--finish-object',
                default=['book'],
                type=list,
                nargs='+', 
                help=(
                        'list of strings with the objects,'
                        'when find one of those the program finish'
                    )
            )
        self.duration = self.get_argument(
                '-d',  '--duration', 
                type=float, 
                default=20.0,
                help='model running duration'
            )
            

    def callback_all_objects(self, detections, image):
        if detections:
            image = draw_on_image(image=image, last_predictions=detections)
        show_image(img=image, title='Video from Gary\'s camera')

# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
from raya.handlers.cv.detectors.tags_detector_handler import \
                                                            TagsDetectorHandler
from raya.tools.image import show_image, draw_on_image


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Tag Detection Example')

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

        # Establish parameters (only families and tag_size are mandatory).
        model_params = {
                'families' : 'tag36h11',
                'nthreads' : 4,
                'quad_decimate' : 2.0,
                'quad_sigma': 0.0,
                'decode_sharpening' : 0.25,
                'refine_edges' : 1,
                'tag_size' : self.tag_size
            }
    
        # Enable detector
        self.log.info('Enabling model...')
        self.detector: TagsDetectorHandler = await self.cv.enable_model(
                model='detector',type='tag',
                name='apriltags', 
                source=self.working_camera,
                model_params = model_params
            )

        self.log.info('Model enabled')
        
        # Create listener
        await self.detector.find_tags(
                tags=self.detect_tags, 
                callback=self.callback_specific_tags
            )
        self.detector.set_img_detections_callback(
                callback=self.callback_all_predictions,
                as_dict=True,
                call_without_detections=True,
                cameras_controller=self.cameras
            )


    async def loop(self):
        resp = await self.detector.find_tags(
                tags=self.finish_tags, 
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
        await self.cameras.disable_color_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='apriltags',
                help='tag model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )
        self.detect_tags = self.get_argument(
                '-dt', '--detect_tags',
                default=['tag36h11.43','tag36h11.1'],
                type=list,
                nargs='+', 
                help='dict of list with the tags to detect in not blockin mode'
            )
        self.finish_tags = self.get_argument(
                '-f', '--finish_tags',
                default=['tag36h11.0'],
                type=list,
                nargs='+', 
                help=(
                    'dict of list with the tags, when find one of those the '
                    'program finish'
                    )
            )
        self.tag_size = self.get_argument(
                '-ts',  '--tag_size', 
                type=float, 
                default=0.06,
                help='tag size in meters'
            )
        self.duration = self.get_argument(
                '-d',  '--duration', 
                type=float, 
                default=10.0,
                help='model running duration'
            )
        self.detect_tags = self.create_dict_arg(self.detect_tags)
        self.finish_tags = self.create_dict_arg(self.finish_tags)


    def callback_specific_tags(self, detected_tag, tag_info, timestamp):
        self.log.info(f'!!!!')
        self.log.info(f'Tag {detected_tag} detected')
        self.log.info(f'Tag info type: {type(tag_info)}')
        self.log.info(f'Tag timestamp {timestamp}')
        self.log.info(f'!!!!')


    def callback_all_predictions(self, detections, image):
        if detections:
            image = draw_on_image(
                    image=image, 
                    last_predictions=detections
                )
        show_image(img=image, title='Video from Gary\'s camera')


    def create_dict_arg(self, arg_list):
        dict_r = {}
        for dt in arg_list:
            if dt.split('.')[0] in dict_r:
                dict_r[dt.split('.')[0]].append(int(dt.split('.')[1]))   
            else: 
                dict_r[dt.split('.')[0]] = [int(dt.split('.')[1])]
        return dict_r

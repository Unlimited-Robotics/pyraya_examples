# System Imports
import threading
from copy import deepcopy

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController


class RayaApplication(RayaApplicationBase):

    async def setup(self): 
        self.key = ''
        self.face = False
        # Call Cameras Controller
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.available_cameras = self.cameras.available_cameras()
        self.working_camera = None
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

        # If a camera name was set
        if self.camera != None:
            cams = set(self.available_cameras)
            if self.camera in cams:
                self.working_camera = self.camera
            else:
                self.log.warn('Camera name not available')
                self.finish_app()
                return
        else:
            self.log.warn('Not camera requested')
            self.finish_app()

        # Enable camera
        await self.cameras.enable_camera(self.working_camera)
        # Create listener
        self.cameras.create_frame_listener(
                                        camera_name=self.working_camera,
                                        callback=self.callback_color_frame)
        # Enable detector
        self.log.info('Enabling model...')
        self.detector = await self.cv.enable_model(
                name='cnn_face',
                source=self.working_camera
            )
        self.log.info('Model enabled')
        self.detector.set_detections_callback(
                callback=self.callback_all_faces,
                as_dict=True,
                call_without_detections=True,
            )
        self.log.warn(f'Please, see the {self.camera} camera...')


    async def loop(self):
        photos = []
        await self.sleep(1.5)
        if not self.face:
            self.log.warn(f'Not face in front of the camera')
            await self.sleep(0.5)
        else:    
            for i in range(5):
                self.log.warn(f'Taking photo {i}')
                photo = await self.take_photo()
                photos.append(photo)
                await self.sleep(1)
            self.kthread = KeyboardThread(self.key_callback)
            self.log.info('Insert your name: ')
            while not self.key:
                await self.sleep(1) 
            name = self.key
            self.log.info(f'Training {name} face...'
                          f' It could take some minutes...')
            model_params = {}
            self.recognizer = await self.cv.train_model(
                    model = 'recognizer',
                    type = 'face',
                    model_name = self.model,
                    images = [photos],
                    names = [name],
                    model_params = model_params
                )
            faces = self.recognizer['faces']
            self.log.info(f'Faces available: {faces}')
            self.finish_app()


    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model='detector', type='face')
        self.log.info('Finish app called')


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
        

    def callback_all_faces(self, detections):
        self.last_detections = list(detections.values())
        if len(self.last_detections) == 1:
            self.face = True
        elif len(self.last_detections) > 1:
            self.log.warn(f'More of one face in front of the camera')


    def key_callback(self, inp):
        self.key = inp


    def callback_color_frame(self, img):
        self.img = img


    async def take_photo(self):
        await self.sleep(0.5)
        photo = deepcopy(self.img)
        # cv2.imshow('img', photo)
        # cv2.waitKey(1000)
        return photo


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()


    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return
            break

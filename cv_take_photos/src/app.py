# System imports
import cv2
import os
import shutil
import threading

# Raya imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.tools.image import show_image


class RayaApplication(RayaApplicationBase):

    async def setup(self): 
        self.kthread = KeyboardThread(self.key_callback)
        self.key = 0
        self.count = 0
        self.folder = 'robot_imgs'
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
            os.makedirs(self.folder)
        else:    
            os.makedirs(self.folder)
        # Call Cameras Controller
        self.cameras: CamerasController = \
                                    await self.enable_controller('cameras')
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
                callback=self.callback_color_frame
            )
        

    async def loop(self):
        try:
            if self.key == 's':
                cv2.imwrite(
                        filename=f'{self.folder}/img_{self.count}.png', 
                        img=self.img)
                self.count += 1
        except:
            import traceback
            self.log.error(traceback.format_exc())
        self.key = 0    


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )


    def key_callback(self, inp):
        self.key = inp


    def callback_color_frame(self, img):
        self.img = img
        show_image(img=img, title='Video from Gary\'s camera', scale=0.4)


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()


    def run(self):
        while True:
            self.input_cbk(input()) 

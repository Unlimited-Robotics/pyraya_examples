from functools import partial

from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.motion_controller import MotionController
from raya.tools.image import show_image


CAMERAS = ['nav_bottom', 'nav_top', 'cv_top']


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling cameras controller')
        self.cameras: CamerasController = \
                                    await self.enable_controller('cameras')

        for camera in CAMERAS:
            self.log.info(f'Enabling camera \'{camera}\'...')
            await self.cameras.enable_color_camera(camera_name=camera)
            self.cameras.create_color_frame_listener(
                    camera_name=camera,
                    callback=partial(self.cb_frame, camera)
                )
            self.log.info(f'Camera \'{camera}\' enabled')


    async def loop(self):
        pass


    async def finish(self):
        for camera in CAMERAS:
            self.log.info(f'Disabling camera \'{camera}\'...')
            await self.cameras.disable_color_camera(camera)
            self.log.info(f'Camera \'{camera}\' disabled')
        self.log.info('App finished')


    def cb_frame(self, camera, img):
        show_image(
            img=img, 
            title=f'Camera {camera}', 
            scale=0.5,
        )

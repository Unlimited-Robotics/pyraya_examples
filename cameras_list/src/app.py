from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.cameras:CamerasController = \
                await self.enable_controller('cameras')
        available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        for camera in available_cameras:
            self.log.info(f'  - {camera}')


    async def loop(self):
        self.finish_app()
        

    async def finish(self):
        pass

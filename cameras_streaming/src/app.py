from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController


LOOP_PERIOD = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        if self.camera_name is None:
            self.log.error(f'Camera argument not defined')
            self.finish_app()
            return
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        port, protocol, path = \
                await self.cameras.enable_streaming(
                    camera_name=self.camera_name)
        self.log.info(f'Enabling camera \'{self.camera_name}\'')
        self.log.info(f'  - Port: {port}')
        self.log.info(f'  - Potocol: {protocol}')
        self.log.info(f'  - Path: publish/{path}')
        self.log.info('')
        self.log.info(f'Check env file to change server, port and more!')
        self.log.info('')
        self.log.info(f'If you have ffmpeg installed in your local machine, ')
        self.log.info(f'you can create a server to send the camera stream')
        self.log.info(f'  ffplay \'{protocol}://:{port}?streamid=publish/'
                      f'{path}&mode=listener\'')
        self.log.info(f'Remember create the server before running the example')
        self.log.info('')
        self.log.info(f'You can install ffmpeg in your ubuntu machine with:')
        self.log.info(f'  sudo apt-get install ffmpeg')


    async def loop(self):
        pass
        

    async def finish(self):
        if self.camera_name is not None:
            await self.cameras.disable_streaming(camera_name=self.camera_name)
            self.log.info(f'Streaming disabled')


    def get_arguments(self):
        self.camera_name = self.get_argument(
                '-c', '--camera-name',
                help='name of camera to stream',
                required=True,
            )

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
        self.log.info(f'The route to locally access the stream is:')
        self.log.info(f'  {protocol}://localhost:{port}{path}')
        self.log.info('')
        self.log.info(f'The route to remotely access the stream is:')
        self.log.info(f'  {protocol}://<ROBOT_IP>:{port}{path}')
        self.log.info('')
        self.log.info(f'If you have ffmpeg installed in your machine, you can')
        self.log.info(f'connect to the streaming with one ot these commands')
        self.log.info(f'  ffplay {protocol}://localhost:{port}?streamid='
                      f'publish/{path}&mode=listener')
        self.log.info(f'  ffplay {protocol}://<ROBOT_IP>:{port}?streamid='
                      f'publish/{path}&mode=listener')
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

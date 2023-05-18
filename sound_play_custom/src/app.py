from raya.application_base import RayaApplicationBase
from raya.controllers.sound_controller import SoundController


AUDIO_PATH = 'res:10sec.wav'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'App started')
        self.sound: SoundController = await self.enable_controller('sound')


    async def loop(self):
        self.log.info(f'Play sound started')
        await self.sound.play_sound(
                path=AUDIO_PATH, 
                volume=self.volume, 
                wait=True,
            )
        self.log.info(f'Play sound finished')
        self.finish_app()


    async def finish(self):
        self.log.info(f'App finished')


    def get_arguments(self):
        self.volume = self.get_argument(
                '-v', '--volume',
                type=int,
                help='volume',
                default=100,
            )

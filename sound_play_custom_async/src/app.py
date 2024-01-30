from raya.application_base import RayaApplicationBase
from raya.controllers.sound_controller import SoundController
import time

AUDIO_PATH = 'res:10sec.wav'
AUDIO_PATH_2 = 'res:kirby.wav'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'App started')
        self.sound: SoundController = await self.enable_controller('sound')
        
        self.log.info(f'playing sound {AUDIO_PATH}')
        await self.sound.play_sound(
                path=AUDIO_PATH, 
                volume=self.volume, 
                callback_feedback=self.sound_callback,
                callback_finish=self.sound_callback_finish,
                wait=False,
            )
        
        self.log.info(f'playing sound {AUDIO_PATH_2}')
        await self.sound.play_sound(
                path=AUDIO_PATH_2, 
                volume=self.volume, 
                callback_feedback=self.sound_callback,
                callback_finish=self.sound_callback_finish,
                wait=False,
            )


    async def loop(self):
        if not self.sound.is_playing():
            self.finish_app()


    async def finish(self):
        if self.sound.is_playing():
            self.log.info('Canceling all sounds')
            await self.sound.cancel_all_sounds()


    def get_arguments(self):
        self.volume = self.get_argument(
                '-v', '--volume',
                type=int,
                help='volume',
                default=100,
            )


    def sound_callback(self, code, msg, time_left):
        self.log.debug(
            f'Sound callback feedback:\n'
                f'\t code:{code}\n'
                f'\t message:{msg}\n'
                f'\t time left: {time_left} seconds'
            )


    def sound_callback_finish(self, code, msg):
        self.log.debug(
            f'Sound callback finish:\n'
                f'\t code:{code}\n'
                f'\t message:{msg}'
            )

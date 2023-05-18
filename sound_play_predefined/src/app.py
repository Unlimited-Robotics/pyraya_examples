import random

from raya.application_base import RayaApplicationBase
from raya.controllers.sound_controller import SoundController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.sound: SoundController = await self.enable_controller('sound')


    async def loop(self):
        self.available_sounds = self.sound.get_predefined_sounds()
        self.log.info(f'Available sounds: {self.available_sounds}')

        if not self.sound_name:
            self.sound_name = random.choice(self.available_sounds)
            self.log.info(f'Playing random sound: {self.sound_name}')
        else:
            if self.sound_name not in self.available_sounds:
                self.log.error(
                        f'Sound name \'{self.sound_name}\' not recognized'
                    )
                self.finish_app()
            self.log.info(f'Playing sound: {self.sound_name}')
        
        await self.sound.play_sound(name=self.sound_name)
        self.finish_app()


    async def finish(self):
        pass

    
    def get_arguments(self):
        self.sound_name = self.get_argument(
                '-s', '--sound-name',
                help='name of the predefined sound to play',
                default='',
            )

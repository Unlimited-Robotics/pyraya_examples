from raya.application_base import RayaApplicationBase
from raya.controllers.sound_controller import SoundController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.sound: SoundController = await self.enable_controller('sound')


    async def loop(self):
        self.log.warn(f'Recording for {self.duration} seconds...')
        record = await self.sound.record_sound(
                duration=self.duration, 
                wait=True
            )
        self.log.warn('Record Finish')

        self.log.warn(f'Playing recording')
        await self.sound.play_sound(
                data=record, 
                volume=self.volume,
            )
        self.finish_app()


    async def finish(self):
        self.log.info(f'Hello from finish()')


    def get_arguments(self):
        self.duration = self.get_argument(
                '-d', '--duration',
                type=float,
                help='time to record',
                default=10.0,
            )
        self.volume = self.get_argument(
                '-v', '--volume',
                type=int,
                help='volume',
                default=100,
            )

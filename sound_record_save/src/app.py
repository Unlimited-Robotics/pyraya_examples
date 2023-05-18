from raya.application_base import RayaApplicationBase
from raya.controllers.sound_controller import SoundController


DURATION = 10.0
NAME_RECORD = 'dat:record.wav'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.sound: SoundController = await self.enable_controller('sound')


    async def loop(self):
        self.log.warn((
                f'Recording for {DURATION} seconds in the file {NAME_RECORD}'
            ))
        await self.sound.record_sound(
                duration=DURATION,
                path=NAME_RECORD,
                wait=True,
            )
        self.finish_app()


    async def finish(self):
        self.log.info(f'Hello from finish()')

import time

from raya.application_base import RayaApplicationBase


LOOP_DELAY = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Setup')
        self.initial_time = time.time()


    async def loop(self):
        self.log.info('Loop')
        await self.sleep(LOOP_DELAY)
        if time.time() - self.initial_time > self.duration:
            self.finish_app()


    async def finish(self):
        self.log.info('Finish')


    def get_arguments(self):
        self.duration = self.get_argument(
                '-d', '--duration', 
                type=float,
                default=10.0,
                help='duration of the application in seconds',
            )

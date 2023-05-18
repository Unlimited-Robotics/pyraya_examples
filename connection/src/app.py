from raya.application_base import RayaApplicationBase


LOOP_DELAY = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Setup')
        self.i = 0


    async def loop(self):
        self.log.info('Loop')
        await self.sleep(LOOP_DELAY)
        self.i += 1
        if self.i==30:
            self.finish_app()


    async def finish(self):
        self.log.info('Finish')

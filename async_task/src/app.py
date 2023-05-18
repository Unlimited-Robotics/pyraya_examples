from raya.application_base import RayaApplicationBase


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0


    async def loop(self):

        if self.i == 0:
            self.create_task(name='task1', afunc=self.task1, par1='argument')
            self.log.info('Task 1 created')

        self.log.info(f'Hello from loop: {self.i}')
        await self.sleep(1.0)
        self.i += 1

        if not self.is_task_running('task1'):
            ret = self.pop_task_return('task1')
            self.log.info('Task 1 finished')
            self.finish_app()
            

    async def finish(self):
        self.log.info('App finished')


    async def task1(self, par1):
        for i in range(10):
            self.log.warn(f'Hello from task: {par1} {i}')
            await self.sleep(0.5)

from raya.application_base import RayaApplicationBase
from raya.controllers.status_controller import StatusController
from raya.enumerations import ANGLE_UNIT, POSITION_UNIT

TIME_TASK_APPS_STATUS = 1
TIME_TASK_RAYA_STATUS = 2
TIME_TASK_ARMS_STATUS = 3
TIME_TASK_BATTERY_STATUS = 4
TIME_TASK_LOCALIZATION_STATUS = 5
TIME_TASK_MANIPULATION_STATUS = 6


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Hello from setup()')
        self.status: StatusController = await self.enable_controller('status')


    async def loop(self):
        self.create_task(name='taskRayaStatus', afunc=self.taskRayaStatus)
        self.create_task(name='taskLocalizationStatus', afunc=self.taskLocalizationStatus)
        while True:
            await self.sleep(1)
    

    async def finish(self):
        self.cancel_task('taskRayaStatus')
        self.cancel_task('taskLocalizationStatus')
        self.log.warn(f'Hello from finish()')


    async def taskRayaStatus(self):
        while True:
            raya_status = await self.status.get_raya_status()
            self.log.info(f'raya status: {raya_status}')
            await self.sleep(TIME_TASK_RAYA_STATUS)

    
    async def taskLocalizationStatus(self):
        while True:
            localization_status = await self.status.get_localization_status(
                    ang_unit=ANGLE_UNIT.DEGREES,
                    pos_unit=POSITION_UNIT.METERS,
                )
            self.log.info(f'localization status: {localization_status}')
            await self.sleep(TIME_TASK_LOCALIZATION_STATUS)
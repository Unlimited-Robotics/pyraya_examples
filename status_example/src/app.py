from raya.application_base import RayaApplicationBase
from raya.controllers.status_controller import StatusController
from raya.enumerations import ANG_UNIT, POS_UNIT

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
        self.create_task(name='taskAppsStatus', afunc=self.taskAppsStatus)
        self.create_task(name='taskRayaStatus', afunc=self.taskRayaStatus)
        self.create_task(
                name='taskLocalizationStatus', 
                afunc=self.taskLocalizationStatus
            )
        self.create_task(
                name='taskBatteryStatus', 
                afunc=self.taskBatteryStatus
            )
        self.create_task(
                name='taskAvailableArmsStatus',
                afunc=self.taskAvailableArmsStatus
            )
        self.create_task(
                name='taskManipulationStatus',
                afunc=self.taskManipulationStatus
            )
        
        while True:
            await self.sleep(1)
    

    async def finish(self):
        self.cancel_task('taskAppsStatus')
        self.cancel_task('taskRayaStatus')
        self.cancel_task('taskLocalizationStatus')
        self.cancel_task('taskBatteryStatus')
        self.cancel_task('taskAvailableArmsStatus')
        self.cancel_task('taskManipulationStatus')
        self.log.warn(f'Hello from finish()')


    async def taskAppsStatus(self):
        while True:
            apps_status = await self.status._get_apps_status()
            self.log.info(f'apps status: {apps_status}')
            await self.sleep(TIME_TASK_APPS_STATUS)
            
            
    async def taskRayaStatus(self):
        while True:
            raya_status = await self.status.get_raya_status()
            self.log.info(f'raya status: {raya_status}')
            await self.sleep(TIME_TASK_RAYA_STATUS)


    async def taskAvailableArmsStatus(self):
        while True:
            arms_status = await self.status.get_available_arms()
            self.log.info(f'available arms status: {arms_status}')
            await self.sleep(TIME_TASK_ARMS_STATUS)
    
    
    async def taskBatteryStatus(self):
        while True:
            battery_status = await self.status.get_battery_status()
            self.log.info(f'battery status: {battery_status}')
            await self.sleep(TIME_TASK_BATTERY_STATUS)
            
    
    async def taskLocalizationStatus(self):
        while True:
            localization_status = await self.status.get_localization_status(
                    ang_unit=ANG_UNIT.DEG,
                    pos_unit=POS_UNIT.METERS,
                )
            self.log.info(f'localization status: {localization_status}')
            await self.sleep(TIME_TASK_LOCALIZATION_STATUS)
            
    
    async def taskManipulationStatus(self):
        while True:
            manipulation_status = await self.status.get_manipulation_status()
            self.log.info(f'manipulation status: {manipulation_status}')
            await self.sleep(TIME_TASK_MANIPULATION_STATUS)

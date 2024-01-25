from raya.application_base import RayaApplicationBase
from raya.controllers.fleet_controller import FleetController
from raya.enumerations import *


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.fleet: FleetController = await self.enable_controller('fleet')
        self.log.warn(f'Hello from setup()')
        self.log.info('The app location selected is: ')
        self.log.info(f'Location x: {self.location_x}')
        self.log.info(f'Location y: {self.location_y}')
        self.log.info(f'Location angle: {self.location_angle}')


    async def loop(self):
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.INFO,
                message='checking fleet info'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.WARNING,
                message='checking fleet Warning'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.ERROR,
                message='checking fleet ERROR'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.SUCCESS,
                message='checking fleet succsess'
            )
        await self.sleep(3.0)
        await self.fleet.finish_task(
                result=FLEET_FINISH_STATUS.SUCCESS,
                message='checking fleet finish succsess'
            )
        await self.sleep(3.0)
        await self.fleet.finish_task(
                result=FLEET_FINISH_STATUS.FAILED,
                message='checking fleet finish FAILED'
            )
        await self.sleep(3.0)
        self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')


    def get_arguments(self):
        self.location_x = self.get_argument(
            '-x', '--target_x',
                type=float,
                help='x of the target',
            )
        self.location_y = self.get_argument(
                '-y', '--target_y',
                type=float,
                help='y of the target',
            )
        self.location_angle = self.get_argument(
                '-a', '--target_angle',
                type=float,
                help='angle of the target',
            )

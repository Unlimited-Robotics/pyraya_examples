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
                message='Testing fleet: INFO'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.WARNING,
                message='Testing fleet: WARNING'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.ERROR,
                message='Testing fleet: ERROR'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                status=FLEET_UPDATE_STATUS.SUCCESS,
                message='Testing fleet: SUCCESS'
            )
        await self.sleep(3.0)
        self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')

        await self.fleet.finish_task(
                result=FLEET_FINISH_STATUS.SUCCESS,
                message='Testing fleet: finish SUCCESS'
            )
        await self.sleep(3.0)
        await self.fleet.finish_task(
                result=FLEET_FINISH_STATUS.FAILED,
                message='Testing fleet: finish FAILED'
            )
        await self.sleep(3.0)


    def get_arguments(self):
        self.location_x = self.get_argument(
            '-x', '--target_x',
                type=float,
                help='x of the target',
                default=0.0,
            )
        self.location_y = self.get_argument(
                '-y', '--target_y',
                type=float,
                help='y of the target',
                default=0.0,
            )
        self.location_angle = self.get_argument(
                '-a', '--target_angle',
                type=float,
                help='angle of the target',
                default=0.0,
            )

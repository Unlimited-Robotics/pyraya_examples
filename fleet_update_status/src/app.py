from raya.application_base import RayaApplicationBase
from raya.controllers.fleet_controller import FleetController
from raya.enumerations import *


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.fleet: FleetController = await self.enable_controller('fleet')
        self.log.info(f'Hello from setup()')


    async def loop(self):
        await self.fleet.update_app_status(
                task_id=self.task_id,
                status=UPDATE_STATUS.INFO,
                message='checking fleet info'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                task_id=self.task_id,
                status=UPDATE_STATUS.WARNING,
                message='checking fleet Warning'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                task_id=self.task_id,
                status=UPDATE_STATUS.ERROR,
                message='checking fleet ERROR'
            )
        await self.sleep(3.0)
        await self.fleet.update_app_status(
                task_id=self.task_id,
                status=UPDATE_STATUS.SUCCESS,
                message='checking fleet succsess'
            )
        await self.sleep(3.0)
        await self.fleet.finish_task(
                task_id=self.task_id,
                result=FINISH_STATUS.SUCCESS,
                message='checking fleet finish succsess'
            )
        await self.sleep(3.0)
        await self.fleet.finish_task(
                task_id=self.task_id,
                result=FINISH_STATUS.FAILED,
                message='checking fleet finish FAILED'
            )
        await self.sleep(3.0)
        self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')


    def get_arguments(self):
        self.target_x = self.get_argument(
            '-x', '--target_x',
                type=float,
                help='x of the target',
                required=True
            )
        self.target_y = self.get_argument(
                '-y', '--target_y',
                type=float,
                help='y of the target',
                required=True
            )
        self.target_angel = self.get_argument(
                '-a', '--target_angle',
                type=float,
                help='angle of the target',
                required=True
            )
        self.object = self.get_argument(
                '-tid', '--task_id',
                type=str,
                help='Fleet management Task Id',
                required=True
            )

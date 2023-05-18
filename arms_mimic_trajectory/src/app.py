from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController

from src.constants import *

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms: ArmsController = await self.enable_controller('arms')


    async def loop(self):

        await self.go_home()

        await self.mimic_predefined_pose(name='pre_pick')
        await self.mimic_predefined_pose(name='pick', constraints=True)
        await self.mimic_predefined_pose(name='nav_with_tray')

        await self.go_home()

        self.finish_app()


    async def go_home(self):
        self.log.info('Going home...')
        await self.arms.set_predefined_pose(
                arm='right_arm',
                predefined_pose='home',
                wait=True,
            )
        await self.arms.set_predefined_pose(
                arm='left_arm',
                predefined_pose='home',
                wait=True,
            )
        await self.sleep(0.2)


    async def mimic_predefined_pose(self, name, constraints=False, plan=True):
        self.log.info(f'Mimic of pose \'{name}\'...')
        if plan:
            res = await self.arms.is_pose_valid(
                'right_arm', 
                **(PREDEFINED_POSES[name]),
                use_obstacles=True,
                update_obstacles=True,
                cartesian_path=False,
                tilt_constraint=constraints,
                save_trajectory=True,
                name_trajectory=name,
                wait=True)

        await self.arms.execute_predefined_trajectory(
            name,
            use_obstacles=False,
            additional_options={'mimic': True, 'mimic_group': 'both'},
            wait=True,
        )

        await self.sleep(0.2)

    async def finish(self):
        self.log.info('Application finished')

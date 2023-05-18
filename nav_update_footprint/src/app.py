from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):

        self.nav: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info(f'Trying to update footprint...')
        await self.nav.update_robot_footprint([
                [-0.5,0.40],[0.5,0.40],[0.25, -0.640],[-0.25, -0.640]
            ])
        self.log.info(f'Footprint updated...')


    async def loop(self):
        self.finish_app()


    async def finish(self):
        pass


from raya.enumerations import *
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=None,
                callback_finish=None
            )
        response = await self.navigation.change_costmap(
            costmap_name=self.costmap_name
            )


        self.log.info((
                'Response costmap change = '
                f'\'{response}\''
            ))


    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('App finished')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the map',
                required=True
            )
        self.costmap_name = self.get_argument(
                '-c', '--costmap-name',
                type=str,
                help='name of the costmap',
                required=True
            )

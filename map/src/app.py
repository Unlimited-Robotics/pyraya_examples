from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling navigation controller')
        self.navigation: NavigationController = \
                            await self.enable_controller('navigation')
        self.log.info(f'Wait, starting mapping...')
        await self.navigation.start_mapping(map_name=self.map_name)
        self.log.info(f'Mapping with map name \'{self.map_name}\'')


    async def loop(self):
        pass


    async def finish(self):
        self.log.info(f'Mapping finished, saving map...')
        await self.navigation.stop_mapping(save_map=not self.no_save_map)
        self.log.info(f'Map saved successfully')
        self.log.info('App finished')
    

    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )
        self.no_save_map = self.get_flag_argument(
                '-ns', '--no-save-map',
                help='use if you don\'t want to save the map',
            )

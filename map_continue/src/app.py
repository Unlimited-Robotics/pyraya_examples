from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling navigation controller')
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info(f'Wait, starting continue mapping...')
        await self.navigation.continue_mapping(
                options={
                        'use_tags': True,
                        'marker_length':  float(self.tag_size),
                        'marker_family': '36h10',
                        'marker_max_range': 3.0
                    }, 
                map_name=self.map_name
            )
        self.log.info(f'Continue mapping with map \'{self.map_name}\'')


    async def loop(self):
        pass


    async def finish(self):
        selected = False
        while not selected:
            selection = input(
                    "Please press Y to save the map or N to ignore the map:"
                )
            selected = True
            if selection.upper() == 'Y':
                self.log.info(f'Saving map...')
                self.save_map = True
            elif selection.upper() == 'N':
                self.log.info(f'Ignoring map...')
                self.save_map = False
            else:
                self.log.info(f'')
                selected = False
        await self.navigation.stop_mapping(save_map = self.save_map)
        self.log.info(f'Mapping procces finished successfully')
    

    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )
        self.tag_size = self.get_argument(
                '-s', '--tag-size',
                type=float,
                help='size of the apriltags to map',
                required=True
            )

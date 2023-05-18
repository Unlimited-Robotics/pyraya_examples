from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController
from raya.exceptions import RayaNavFileNotFound, RayaNavWrongFileFormat


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.log.info('Trying to generate speed zones files...')
        try:
            await self.navigation.generate_speed_zones_files(
                    map_name=self.map_name
                )
        except (RayaNavFileNotFound, RayaNavWrongFileFormat):
            self.log.error('Error generating files, check map name and files.')
            self.finish_app()
        self.log.info('Files generated...')


    async def loop(self):
        self.finish_app()


    async def finish(self):
        pass


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )


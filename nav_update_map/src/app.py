from raya.enumerations import *
from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController


DOWNLOAD_MAP_PATH = 'dat:downloaded_map.pgm'
UPLOAD_MAP_PATH = 'dat:to_upload_map.pgm'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.nav: NavigationController = \
                await self.enable_controller('navigation')


    async def loop(self):
        if self.upload:
            self.log.info(f'Uploading \'{UPLOAD_MAP_PATH}\' map...')
            await self.nav.update_map(
                    map_name=self.map_name, 
                    path=UPLOAD_MAP_PATH,
                )
            self.log.info(f'Map updated')
        else:
            self.log.info(f'Downloading \'{DOWNLOAD_MAP_PATH}\' map...')
            await self.nav.download_map(
                    map_name=self.map_name, 
                    path=DOWNLOAD_MAP_PATH,
                )
            self.log.info(f'Map downloaded')
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
        self.upload = self.get_flag_argument(
                '-u', '--upload',
                help='if enabled, uploads the map, by default downloads'
            )

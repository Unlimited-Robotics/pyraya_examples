from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController
from raya.enumerations import POSITION_UNIT, ANGLE_UNIT
from raya.exceptions import RayaNavLocationNotFound
from raya.exceptions import RayaNavLocationAlreadyExist


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')

        self.navigation_status = await self.navigation.get_status()

        self.log.info((
                f'Current map = {self.navigation_status["map_name"]}',
                f'Localized = {self.navigation_status["localized"]}'
            ))
        if not self.navigation_status['localized']:
            self.log.error(f'Robot not localized.')
            self.finish_app()
        self.map_name = self.navigation_status['map_name']

        if self.overwrite:
            try: 
                await self.navigation.delete_location( 
                        location_name=self.location_name, 
                        map_name=self.map_name
                    )
                self.log.warn(f'Overwriting location.')
            except RayaNavLocationNotFound:
                self.log.info(f'Saving location.')

        try: 
            await self.navigation.save_location( 
                    location_name=self.location_name, 
                    map_name=self.map_name,
                    current_pose = True,
                    x=0.0, 
                    y=0.0, 
                    angle=0.0,
                )
            self.log.info(f'Location saved')
        except RayaNavLocationAlreadyExist:
            self.log.error('Unable to save location: location already exists.')
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.location_name = self.get_argument(
                '-l', '--location-name',
                type=str,
                help='name of the new location.',
                required=True
            )
        self.overwrite = self.get_flag_argument(
                '-o', '--overwrite',
                help='use if you want to overwrite the location if it exists.',
            )

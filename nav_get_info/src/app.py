from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavLocationNotFound
from raya.exceptions import RayaNavLocationAlreadyExist


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        robot_localized = await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=None,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.list_of_maps = await self.navigation.get_list_of_maps()
        self.log.info(f'Available maps = \'{self.list_of_maps}\'')
        self.navigation_status = await self.navigation.get_status()
        self.log.info((
                'Current navigation status ='
                f'\'{self.navigation_status}\''
            ))

        zones_list = await self.navigation.get_zones(
                map_name='unity_apartment'
            )
        self.log.info(f'list of zones = {zones_list}')

        locations = await self.navigation.get_locations_list(
                map_name='unity_apartment'
            )
        self.log.info(f'list of locations = {locations}')

        zones_info = await self.navigation.get_zones_list(
                map_name='unity_apartment'
            )
        self.log.info(f'info of zones = {zones_info}')

        locations_info = await self.navigation.get_locations(
                map_name='unity_apartment'
            )
        self.log.info(f'info of locations = {locations_info}')

        self.location = await self.navigation.get_location(
                location_name='kitchen', 
                map_name='unity_apartment',
                pos_unit=POS_UNIT.PIXEL
            )
        self.log.info(f'kitchen info= {self.location}')

        kitchen_center = await self.navigation.get_zone_center(
                zone_name='kitchen'
            )
        self.log.info(f'kitchen center = {kitchen_center}')
        try:
            await self.navigation.delete_zone(
                    map_name=self.map_name,
                    location_name='test001'
                )
            self.log.info(f'zone test001 deleted successfully')
        except RayaNavLocationNotFound:
            self.log.error(f'Unable to delete zone: zone not found.')
        try: 
            await self.navigation.delete_location( 
                    location_name='test001', 
                    map_name=self.map_name
                )
            self.log.info(f'Location deleted')
        except RayaNavLocationNotFound:
            self.log.error(f'Unable to delete location: location not found.')
        
        try: 
            await self.navigation.save_location( 
                    x=1.0, 
                    y=0.5, 
                    angle=1.0,
                    location_name='test001', 
                    pos_unit=POS_UNIT.METERS, 
                    ang_unit=ANG_UNIT.RAD, 
                    map_name='unity_apartment'
                )
            self.log.info(f'Location saved')
        except RayaNavLocationAlreadyExist:
            self.log.error('Unable to save location: location already exists.')
        try: 
            await self.navigation.save_zone( 
                    zone_name='test001', 
                    points=[[0, 1],[1, 1],[1, 0],[0, 0]], 
                    pos_unit = POS_UNIT.METERS,
                    map_name = 'unity_apartment',
                    wait=True
                )
            self.log.info(f'Zone saved')
        except RayaNavLocationAlreadyExist:
            self.log.error('Unable to save zone: zone already exists.')
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True
            )

from raya.exceptions import *
from raya.application_base import RayaApplicationBase
from raya.controllers.fleet_controller import FleetController
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.interactions_controller import InteractionsController
from raya.controllers.leds_controller import LedsController
from raya.enumerations import *


class RayaApplication(RayaApplicationBase):
    
    async def setup(self):
        self.objects = {
            'towel': (342.0, 141.0),
            'soap': (0.5, 0.5),
            'linens': (0.5, 0.5),
        }
        self.map_name = 'unity_apartment'

        # Enable controllers
        self.nav: NavigationController = \
                await self.enable_controller('navigation')
        self.fleet: FleetController = await self.enable_controller('fleet')
        self.leds: LedsController = await self.enable_controller('leds')
        self.interactions: InteractionsController = \
                await self.enable_controller('interactions')

        # Navigation settings
        await self.nav.set_map(
                map_name=self.map_name,
                wait_localization=True,
                wait=True,
            )
        await self.sleep(5.0)
        if await self.nav.is_localized():
            self.log.info('Robot is localized')
        else:
            self.log.info('Robot is not localized')
            await self.finish()


    async def loop(self):
        # Navigate to the object position
        try:
            msg_res = await self.fleet.request_action(
                    title='I need help',
                    message=('I am having trouble finding the way, '
                            'can you help me?'),
                    task_id=self.task_id
                )
            if msg_res == 'Ok, coming':
                self.log.info('Message received {mes_res}')
            elif msg_res == 'Abort task':
                self.log.info('Message received {mes_res}')
                await self.finish()
        except RayaFleetTimeout:
            self.log.warn('Timeout exceeded')
            await self.finish()

        if self.object:
            object_x, object_y = self.objects[self.object]
        try:
            res = await self.fleet.get_closest_checkpoint(
                    x=object_x,
                    y=object_y
                )
            nav_x = res[0]
            nav_y = res[1]
        except RayaFleetWrongResponse:
            self.log.warn(f'No checkpoints found')
            await self.finish()
            return
        # Wait until navigation is cleared and then execute it
        await self.preform_navigation(x=nav_x, y=nav_y)
        await self.turn_on_leds(color='blue_general')

        await self.preform_navigation(x=object_x, y=object_y)
        await self.turn_on_leds(color='green_general')
        await self.sleep(10.0)

        try:
            # Navigate to the target goal position, checkpoint first
            res = await self.fleet.get_closest_checkpoint(
                    x=self.target_x,
                    y=self.target_y
                )
            target_x_ch_po = res[0]
            target_y_ch_po = res[1]
        except RayaFleetWrongResponse:
            self.log.warn(f'No checkpoints found')
            await self.finish()
            return
        await self.preform_navigation(x=target_x_ch_po, y=target_y_ch_po)
        await self.turn_on_leds(color='blue_general')

        # Navigate to the target goal position
        await self.preform_navigation(x=self.target_x, y=self.target_y)
        await self.turn_on_leds(color='green_general')

        await self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')
        await self.fleet.finish_task(
                task_id=self.task_id, 
                status=FLEET_FINISH_STATUS.SUCCESS
            )


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
        self.task_id = self.get_argument(
                '-o', '--object',
                type=str,
                help=('To what object is going to navigate, value can be: '
                    '\'towel\',\'soap\',\'linens\''),
                required=True
            )
        self.object = self.get_argument(
                '-t', '--task_id',
                type=str,
                help='Fleet management Task Id',
                required=True
            )


    async def preform_navigation(self, x, y):
        while not await self.fleet.can_navigate(x=x, y=y, wait=True):
            await self.sleep(5.0)
            self.log.info(
                    'Waiting for navigation confirmation from fleet system'
                )
        self.log.info(f'Navigating to {x}, {y}')
        await self.nav.navigate_to_position(
                x=float(x),
                y=float(y),
                angle=90.0,
                wait=True
            )


    async def turn_on_leds(self, color):
        await self.leds.animation(
                group='head',
                color=color,
                animation='task_finished',
                speed=1,
                repetitions=1
            )

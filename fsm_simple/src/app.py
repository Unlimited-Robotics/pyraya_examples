from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.leds_controller import LedsController
from raya.controllers.sound_controller import SoundController
from raya.controllers.ui_controller import UIController
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.sensors_controller import SensorsController
from raya.controllers.arms_controller import ArmsController
from raya.tools.fsm import FSM

from src.static.cameras import *
from src.static.sensors import *


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        # Variables
        self.main_camera = ''
        self.main_temp_sensor = ''
        # Controllers
        self.nav:NavigationController = \
                await self.enable_controller('navigation')
        self.leds:LedsController  = await self.enable_controller('leds')
        self.sound:SoundController = await self.enable_controller('sound')
        self.ui:UIController = await self.enable_controller('ui')
        self.cameras:CamerasController = \
                await self.enable_controller('cameras')
        self.sensors:SensorsController = \
                await self.enable_controller('sensors')
        self.arms:ArmsController = await self.enable_controller('arms')
        # Initializations
        self.simulation = self.is_simulation()
        await self.init_cameras()
        await self.init_sensors()
        await self.init_arms()
        # FSMs
        self.fsm_task1 = FSM(app=self, name='task1', log_transitions=True)


    async def loop(self):
        # tick() returns False if the FSM is finished or aborted
        if not await self.fsm_task1.tick():
            self.finish_app()


    async def finish(self):
        # fsm_error[0]: error code, fsm_error[1]: error message
        fsm_error = self.fsm_task1.get_error()
        if fsm_error[0] == 0:
            self.log.info('App correctly finished')
        else:
            self.log.error(
                    f'App finished with error [{fsm_error[0]}]: {fsm_error[1]}'
                )
            

    def is_simulation(self):
        camera_names = self.cameras.available_color_cameras()
        return 'nav_top' not in camera_names


    async def init_cameras(self):
        self.log.info('Initializing cameras...')
        if self.simulation:
            self.main_camera = CAMERA_SIMULATION
        else:
            self.main_camera = CAMERA_REAL_ROBOT
        await self.cameras.enable_color_camera(self.main_camera)
        self.log.info('Cameras ready')


    async def init_sensors(self):
        self.log.info('Initializing sensors...')
        if self.simulation:
            self.main_temp_sensor = SENSOR_TEMP_SIMULATION
        else:
            self.main_temp_sensor = SENSOR_TEMP_REAL_ROBOT
        self.log.info('Sensors ready')


    async def init_arms(self):
        self.log.info('Initializing arms...')
        if self.simulation:
            await self.arms.set_predefined_pose('both', 'home', wait=True)
        self.log.info('Arms ready')

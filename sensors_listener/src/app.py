from raya.application_base import RayaApplicationBase
from raya.controllers.sensors_controller import SensorsController

from src.constants import *


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.sensors:SensorsController = \
                await self.enable_controller('sensors')
        self.sensors.create_threshold_listener(
                listener_name=LISTENER_NAME,
                callback=self.cb_listener,
                sensors_paths=SENSORS_PATHS,
                lower_bound=28.0
            )


    async def loop(self):
        await self.sleep(1.0)
        self.log.info('Doing other (non blocking) stuff...')


    async def finish(self):
        self.sensors.delete_listener(listener_name=LISTENER_NAME)


    def cb_listener(self):
        self.log.warning('Environment temperature over 28 degrees!')

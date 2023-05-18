import json

from raya.application_base import RayaApplicationBase
from raya.controllers.sensors_controller import SensorsController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.sensors:SensorsController = \
                await self.enable_controller('sensors')
        self.log.info('AVAILABLE SENSORS:')
        self.log.info(json.dumps(
                obj=self.sensors.get_sensors_list(), indent=2
            ))
        self.finish_app()


    async def loop(self):
        pass


    async def finish(self):
        pass

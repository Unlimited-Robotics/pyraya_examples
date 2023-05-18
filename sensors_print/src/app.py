import json

from raya.application_base import RayaApplicationBase
from raya.controllers.sensors_controller import SensorsController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.sensors:SensorsController = \
                await self.enable_controller('sensors')


    async def loop(self):
        sensors_data = self.sensors.get_all_sensors_values()
        self.log.info('')
        self.log.info(f'----------------{self.i}--------------')
        self.log.info(json.dumps(sensors_data, indent=2))
        self.log.info(f'----------------{self.i}--------------')
        await self.sleep(0.5)
        self.i += 1

        
    async def finish(self):
        pass

import json

from raya.application_base import RayaApplicationBase
from raya.controllers.sensors_controller import SensorsController
from raya.exceptions import RayaSensorsNoData


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.sensors:SensorsController = \
                await self.enable_controller('sensors')


    async def loop(self):
        self.log.info('')
        self.log.info(f'----------------{self.i}--------------')
        try:
            sensors_data = self.sensors.get_all_sensors_values()
        except RayaSensorsNoData:
            self.log.info(f'Waiting for data from the robot\'s sensors...')
        self.log.info(json.dumps(sensors_data, indent=2))
        self.log.info(f'----------------{self.i}--------------')
        self.i += 1
        await self.sleep(0.5)

        
    async def finish(self):
        pass

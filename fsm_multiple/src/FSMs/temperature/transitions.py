from raya.tools.fsm import BaseTransitions

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.constants import *


class Transitions(BaseTransitions):

    def __init__(self, app: RayaApplication):
        super().__init__()
        self.app = app

    
    async def HOT(self):
        if self.app.sensors.get_sensor_value(self.app.main_temp_sensor) < \
                TEMPERATURE_HOT:
            self.set_state('FRESH')


    async def FRESH(self):
        if self.app.is_timer_done('FRESH'):
            self.set_state('END')

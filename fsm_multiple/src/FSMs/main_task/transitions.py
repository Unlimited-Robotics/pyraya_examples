from raya.tools.fsm import BaseTransitions

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.constants import *
from src.FSMs.main_task.helpers import Helpers


class Transitions(BaseTransitions):

    def __init__(self, app: RayaApplication, helpers: Helpers):
        super().__init__()
        self.app = app
        self.helpers = helpers


    async def LOCALIZING(self):
        if await self.app.nav.is_localized():
            self.set_state('NAV_TO_HOME')


    async def NAV_TO_HOME(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_navigation_error()
            if nav_error[0] == 0:
                self.set_state('IDLE')
            else:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)


    async def IDLE(self):
        if self.app.sensors.get_sensor_value(self.app.main_temp_sensor) >= \
                TEMPERATURE_HOT:
            self.set_state('TEMPERATURE')
        if self.helpers.last_ui_result is not None:
            clicked_option = \
                    self.helpers.last_ui_result['selected_option']['id']
            if clicked_option==1:
                self.set_state('KITCHEN')
            elif clicked_option==2:
                self.set_state('BEDROOM')
            elif clicked_option==3:
                self.set_state('LAUNDRY')
            else:
                self.set_state('END')

    
    async def TEMPERATURE(self):
        if self.helpers.fsm_temperature.has_finished():
            if self.helpers.fsm_temperature.was_successful():
                self.set_state('IDLE')
            else:
                self.abort(*self.fsm_main_task.get_error())


    async def KITCHEN(self):
        if self.helpers.fsm_kitchen.has_finished():
            if self.helpers.fsm_kitchen.was_successful():
                self.set_state('IDLE')
            else:
                self.abort(*self.fsm_main_task.get_error())


    async def BEDROOM(self):
        if self.helpers.fsm_bedroom.has_finished():
            if self.helpers.fsm_bedroom.was_successful():
                self.set_state('IDLE')
            else:
                self.abort(*self.fsm_main_task.get_error())


    async def LAUNDRY(self):
        if self.helpers.fsm_laundry.has_finished():
            if self.helpers.fsm_laundry.was_successful():
                self.set_state('IDLE')
            else:
                self.abort(*self.fsm_main_task.get_error())

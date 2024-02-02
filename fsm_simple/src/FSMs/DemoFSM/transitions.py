from raya.tools.fsm import BaseTransitions

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.constants import *
from .helpers import Helpers


class Transitions(BaseTransitions):

    def __init__(self, app: RayaApplication, helpers: Helpers):
        super().__init__()
        self.app = app
        self.helpers = helpers


    # If the method is called without calling "self.set_state", the state
    # keep being the same.
    async def LOCALIZING(self):
        if await self.app.nav.is_localized():
            self.set_state('NAV_TO_HOME')


    async def NAV_TO_HOME(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_result()
            # nav_error[0]: error code
            # nav_error[1]: error message
            if nav_error[0] == 0:
                self.set_state('IDLE')
            else:
                # Custom error code and message:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)


    async def IDLE(self):
        if self.app.sensors.get_sensor_value(self.app.main_temp_sensor) >= \
                TEMPERATURE_HOT:
            self.set_state('HOT')
        if self.helpers.last_ui_result is not None:
            clicked_option = \
                    self.helpers.last_ui_result['selected_option']['id']
            if clicked_option==1:
                self.set_state('NAV_TO_KITCHEN')
            elif clicked_option==2:
                self.set_state('NAV_TO_BEDROOM')
            elif clicked_option==3:
                self.set_state('NAV_TO_LAUNDRY')
            else:
                self.set_state('END')

    
    async def HOT(self):
        if self.app.sensors.get_sensor_value(self.app.main_temp_sensor) < \
                TEMPERATURE_HOT:
            self.set_state('FRESH')


    async def FRESH(self):
        if self.app.is_timer_done('FRESH'):
            self.set_state('IDLE')

    
    async def NAV_TO_KITCHEN(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_result()
            if nav_error[0] == 0:
                self.set_state('TAKE_PHOTO')
            else:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)


    async def TAKE_PHOTO(self):
        if self.app.is_timer_done('TAKE_PHOTO'):
            self.set_state('NAV_TO_HOME')


    async def NAV_TO_BEDROOM(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_result()
            if nav_error[0] == 0:
                self.set_state('WAVE')
            else:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)


    async def WAVE(self):
        if self.app.is_task_done('WAVE'):
            self.set_state('NAV_TO_HOME')


    async def NAV_TO_LAUNDRY(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_result()
            if nav_error[0] == 0:
                self.set_state('LOOK_FOR_PANTS')
            else:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)


    async def LOOK_FOR_PANTS(self):
        if self.app.is_timer_done('LOOK_FOR_PANTS'):
            self.set_state('NAV_TO_HOME')

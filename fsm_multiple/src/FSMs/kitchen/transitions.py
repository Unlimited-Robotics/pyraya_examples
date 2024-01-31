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


    async def NAV_TO_HOME(self):
        if not self.app.nav.is_navigating():
            nav_error = self.app.nav.get_last_result()
            if nav_error[0] == 0:
                self.set_state('END')
            else:
                self.abort(*APPERR_COULD_NOT_NAV_TO_HOME)

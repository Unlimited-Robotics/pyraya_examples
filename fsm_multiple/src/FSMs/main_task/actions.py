import cv2
import base64

from raya.tools.fsm import BaseActions

from src.app import RayaApplication
from src.static.navigation import *
from src.static.ui import *
from src.static.constants import *
from src.static.arms import *
from src.FSMs.main_task.helpers import Helpers


class Actions(BaseActions):

    def __init__(self, app: RayaApplication, helpers: Helpers):
        super().__init__()
        self.app = app
        self.helpers = helpers


    async def enter_LOCALIZING(self):
        await self.app.ui.display_screen(**UI_SCREEN_LOCALIZING)
        await self.app.nav.set_map(NAV_MAP_NAME)


    async def LOCALIZING_to_NAV_TO_HOME(self):
        await self.app.ui.display_screen(**UI_SCREEN_FIRST_NAV_TO_HOME)


    async def enter_NAV_TO_HOME(self):
        await self.app.nav.navigate_to_position(
                **NAV_POINT_HOME,
                callback_feedback_async=self.helpers.nav_feedback_async,
            )


    async def enter_IDLE(self):
        self.helpers.last_ui_result = None
        await self.app.ui.display_choice_selector(
                **UI_SELECTOR_WHERE_TO_GO,
                wait=False,
                callback=self.helpers.ui_result_callback,
            )


    async def enter_TEMPERATURE(self):
        await self.helpers.fsm_temperature.run_in_background()


    async def enter_KITCHEN(self):
        await self.helpers.fsm_kitchen.run_in_background()


    async def enter_BEDROOM(self):
        await self.helpers.fsm_bedroom.run_in_background()


    async def enter_LAUNDRY(self):
        await self.helpers.fsm_laundry.run_in_background()


    async def aborted(self, error, msg):
        await self.app.ui.display_screen(
                **UI_SCREEN_FAILED,
                subtitle=f'ERROR {error}: {msg}'
            )
        await self.app.sound.play_sound(name='error')

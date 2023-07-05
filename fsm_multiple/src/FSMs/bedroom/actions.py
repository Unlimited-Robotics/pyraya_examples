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


    async def enter_NAV_TO_BEDROOM(self):
        await self.app.ui.display_screen(**UI_SCREEN_NAV_TO_BEDROOM)
        await self.app.nav.navigate_to_position(**NAV_POINT_BEDROOM)


    async def enter_WAVE(self):
        await self.app.ui.display_screen(**UI_SCREEN_WAVING)
        self.app.create_task(
                name='WAVE', 
                afunc=self.helpers.arm_wave,
            )
        

    async def enter_NAV_TO_HOME(self):
        await self.app.ui.display_screen(**UI_SCREEN_COME_BACK_FROM_BEDROOM)
        await self.app.nav.navigate_to_position(
                **NAV_POINT_HOME,
                callback_feedback_async=self.helpers.nav_feedback_async,
            )

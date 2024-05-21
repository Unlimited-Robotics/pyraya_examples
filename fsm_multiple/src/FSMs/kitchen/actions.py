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


    async def enter_NAV_TO_KITCHEN(self):
        await self.app.ui.display_screen(**UI_SCREEN_NAV_TO_KITCHEN)
        await self.app.nav.navigate_to_position(
                **NAV_POINT_KITCHEN,
                callback_feedback_async=self.helpers.nav_feedback_async,
            )


    async def enter_TAKE_PHOTO(self):
        img = await self.app.cameras.get_next_frame(self.app.main_camera)
        img_enc = cv2.imencode(".jpg", img)[1].tobytes()
        img_base64 = base64.b64encode(img_enc).decode('utf-8')
        await self.app.ui.display_animation(
                **UI_SCREEN_TAKE_PHOTO,
                content = img_base64,
                format = UI_ANIMATION_TYPE.JPEG,
            )
        self.app.create_timer('TAKE_PHOTO', TIME_TAKING_KITCHEN_PHOTO)


    async def enter_NAV_TO_HOME(self):
        await self.app.ui.display_screen(**UI_SCREEN_COME_BACK_WITHOUT_FOOD)
        await self.app.nav.navigate_to_position(
                **NAV_POINT_HOME,
                callback_feedback_async=self.helpers.nav_feedback_async,
            )

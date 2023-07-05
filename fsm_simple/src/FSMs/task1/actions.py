import cv2
import base64

from raya.tools.fsm import BaseActions

from src.app import RayaApplication
from src.static.navigation import *
from src.static.ui import *
from src.static.constants import *
from src.static.arms import *
from src.FSMs.task1.helpers import Helpers


class Actions(BaseActions):

    def __init__(self, app: RayaApplication, helpers: Helpers):
        super().__init__()
        self.app = app
        self.helpers = helpers


    # Action to perform once when the FSM gets the state LOCALIZING
    async def enter_LOCALIZING(self):
        await self.app.ui.display_screen(**UI_SCREEN_LOCALIZING)
        await self.app.nav.set_map(NAV_MAP_NAME)


    # Action to perform once when the FMS goes from LOCALIZING to NAV_TO_HOME
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


    async def enter_HOT(self):
        await self.app.ui.display_screen(**UI_SCREEN_HOT)

    
    async def enter_FRESH(self):
        await self.app.ui.display_screen(**UI_SCREEN_FRESH)
        self.app.create_timer('FRESH', TIME_GETTING_FRESH)


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
            )
        self.app.create_timer('TAKE_PHOTO', TIME_TAKING_KITCHEN_PHOTO)


    # Action to be perfomed when the FSM leaves the state TAKE_PHOTO
    async def leave_TAKE_PHOTO(self):
        await self.app.ui.display_screen(**UI_SCREEN_COME_BACK_WITHOUT_FOOD)


    async def enter_NAV_TO_BEDROOM(self):
        await self.app.ui.display_screen(**UI_SCREEN_NAV_TO_BEDROOM)
        await self.app.nav.navigate_to_position(**NAV_POINT_BEDROOM)


    async def enter_WAVE(self):
        await self.app.ui.display_screen(**UI_SCREEN_WAVING)
        self.app.create_task(
                name='WAVE', 
                afunc=self.helpers.arm_wave,
            )


    async def leave_WAVE(self):
        await self.app.ui.display_screen(**UI_SCREEN_COME_BACK_FROM_BEDROOM)


    async def enter_NAV_TO_LAUNDRY(self):
        await self.app.ui.display_screen(**UI_SCREEN_NAV_TO_LAUNDRY)
        await self.app.nav.navigate_to_position(**NAV_POINT_LAUNDRY)

    
    async def enter_LOOK_FOR_PANTS(self):
        await self.app.ui.display_screen(**UI_SCREEN_LOOK_FOR_PANTS)
        self.app.create_timer('LOOK_FOR_PANTS', TIME_LOOKING_FOR_PANTS)


    async def leave_LOOK_FOR_PANTS(self):
        await self.app.ui.display_screen(**UI_SCREEN_COME_BACK_FROM_LAUNDRY)


    async def enter_END(self):
        await self.app.ui.display_screen(**UI_SCREEN_END)


    # This method is called at the end of execution of the FSM if it was 
    # aborted. Not mandatory method
    async def aborted(self, error, msg):
        await self.app.ui.display_screen(
                **UI_SCREEN_FAILED,
                subtitle=f'ERROR {error}: {msg}'
            )
        await self.app.sound.play_sound(name='error')

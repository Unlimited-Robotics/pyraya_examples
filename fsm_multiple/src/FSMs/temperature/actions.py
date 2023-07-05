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

    def __init__(self, app: RayaApplication):
        super().__init__()
        self.app = app


    async def enter_HOT(self):
        await self.app.ui.display_screen(**UI_SCREEN_HOT)

    
    async def enter_FRESH(self):
        await self.app.ui.display_screen(**UI_SCREEN_FRESH)
        self.app.create_timer('FRESH', TIME_GETTING_FRESH)

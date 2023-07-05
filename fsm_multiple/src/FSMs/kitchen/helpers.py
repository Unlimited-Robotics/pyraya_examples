from raya.exceptions import *

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.arms import *


class Helpers:

    def __init__(self, app: RayaApplication):        
        self.app = app
        # Vabiables
        self.last_ui_result = None

    async def nav_feedback_async(self, code, msg, distance_to_goal, speed):
        if code == 9: # Waiting for obstacle to move
            await self.app.sound.play_sound(name='error')

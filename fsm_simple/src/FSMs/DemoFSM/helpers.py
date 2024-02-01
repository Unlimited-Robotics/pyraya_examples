from raya.exceptions import *

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.arms import *


class Helpers:

    def __init__(self, app: RayaApplication):        
        self.app = app
        # Vabiables
        self.last_ui_result = None


    def ui_result_callback(self, data):
        self.last_ui_result = data


    async def nav_feedback_async(self, code, msg, distance_to_goal, speed):
        if code == 9: # Waiting for obstacle to move
            await self.app.sound.play_sound(name='error')


    async def arm_wave(self):
        await self.app.arms.execute_joints_positions_array(
                **ARMS_WAVE_SEQUENCE, 
                wait=True
            )
        await self.app.arms.set_predefined_pose(
                arm=ARMS_WAVE_ARM,
                predefined_pose='home', 
                wait=True
            )

from raya.exceptions import *
from raya.tools.fsm import FSM

from src.app import RayaApplication
from src.static.app_errors import *
from src.static.arms import *


class Helpers:

    def __init__(self, app: RayaApplication):        
        self.app = app
        # Vabiables
        self.last_ui_result = None
        self.fsm_temperature = FSM(
                app=self.app, 
                name='temperature', 
                log_transitions=True,
            )
        self.fsm_kitchen = FSM(
                app=self.app, 
                name='kitchen', 
                log_transitions=True,
            )
        self.fsm_bedroom = FSM(
                app=self.app, 
                name='bedroom', 
                log_transitions=True,
            )
        self.fsm_laundry = FSM(
                app=self.app, 
                name='laundry', 
                log_transitions=True,
            )


    def ui_result_callback(self, data):
        self.last_ui_result = data


    async def nav_feedback_async(self, code, msg, distance_to_goal, speed):
        if code == 9: # Waiting for obstacle to move
            await self.app.sound.play_sound(name='error')

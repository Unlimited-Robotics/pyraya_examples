import re

from raya.controllers.ui_controller import UIController
from raya.controllers.motion_controller import MotionController

from raya.tools.filesystem import delete_dat_file
from raya.exceptions import *

from src.tools.ui import ui_countdown, ui_list_of_files
from src.static.ui.general import *
from src.static.ui.motion import *
from src.static.fs import *
from src.static.motion import *


class MotionHandler():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui


    async def init(self):
        self.motion:MotionController = \
                await self.app.enable_controller('motion')

    
    async def main_display(self, default_selection=-1):
        while True:
            if default_selection == -1:
                response = await self.ui.display_choice_selector(
                        **UI_MOTION_MAIN_SELECTOR
                    )
                if response['action'] == 'back_pressed':
                    return
                selection = response['selected_option']['id']
            else:
                selection = default_selection
            if selection==1:
                await self.rotate(ROTATE_DIR.RIGHT)
            if selection==2:
                await self.rotate(ROTATE_DIR.LEFT)
            if selection==3:
                await self.move_linear(MOVING_DIR.FORWARD)
            if selection==4:
                await self.move_linear(MOVING_DIR.BACKWARD)


    async def rotate(self, direction):
        await self.ui.display_screen(**UI_MOTION_ROTATING)
        await self.motion.rotate(
                angle=90.0, 
                angular_speed=20.0*(1 if direction == ROTATE_DIR.LEFT else -1), 
                wait=True, 
                enable_obstacles=False
            )
        # List available predefined sounds in the UI controller.

    async def move_linear(self, direction):
        await self.ui.display_screen(**UI_MOTION_MOVING)
        await self.motion.move_linear(
                distance=1.0, 
                x_velocity=0.3*(1 if direction == MOVING_DIR.FORWARD else -1),
                wait=True
            )



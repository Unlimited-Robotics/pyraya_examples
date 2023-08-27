import re

from raya.controllers.ui_controller import UIController
from raya.controllers.leds_controller import LedsController

from raya.tools.filesystem import delete_dat_file
from raya.exceptions import *

from src.tools.ui import ui_countdown, ui_list_of_files
from src.static.ui.general import *
from src.static.ui.leds import *
from src.static.fs import *


class LedsHandler():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui


    async def init(self):
        self.leds:LedsController = await self.app.enable_controller('leds')

    
    async def main_display(self, default_selection=-1):
        while True:
            if default_selection == -1:
                response = await self.ui.display_choice_selector(
                        **UI_LEDS_MAIN_SELECTOR
                    )
                if response['action'] == 'back_pressed':
                    return
                selection = response['selected_option']['id']
            else:
                selection = default_selection
            if selection==1:
                await self.display_animation('motion_1', 'blue')
            if selection==2:
                await self.display_animation('motion_4', 'blue')
            if selection==3:
                await self.display_animation('motion_10_ver_3', 'green')
         

    async def display_animation(self, animation='motion_4', color='blue'):
        # await self.ui.display_screen(**UI_MOTION_ROTATING)
        await self.leds.animation(
                    group='head', 
                    color=color, 
                    animation=animation, 
                    speed=9, 
                    repetitions=4, 
                    # execution_control = EXECUTION_CONTROL.OVERRIDE,
                    wait=False
                )


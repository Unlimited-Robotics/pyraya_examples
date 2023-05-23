from copy import deepcopy

from raya.controllers.ui_controller import UIController
from raya.controllers.sound_controller import SoundController

from src.static.ui import *


class SoundUI():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui


    async def init(self):
        self.sound:SoundController = await self.app.enable_controller('sound')

    
    async def main_display(self):
        response = await self.ui.display_choice_selector(
                **UI_SOUND_MAIN_DISPLAY
            )
        if response['action'] == 'back_pressed':
            return
        selection = response['selected_option']['id']
        if selection==1:
            await self.play_predefined_sound()


    async def play_predefined_sound(self):
        sound_names = self.sound.get_predefined_sounds()
        print(sound_names)
        ui_display = deepcopy(UI_SOUND_PLAY_PREDEFINED)
        print(ui_display)
        for i, sound_name in enumerate(sound_names):
            print(sound_name)
            ui_display['data'].append({'id':i, 'name': sound_name})
        print(ui_display)
        response = await self.ui.display_choice_selector(**ui_display)
        print(response)
            


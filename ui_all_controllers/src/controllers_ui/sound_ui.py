from raya.controllers.ui_controller import UIController
from raya.controllers.sound_controller import SoundController
from raya.tools.filesystem import list_files_in_folder, create_dat_folder
from raya.exceptions import *

from src.static.ui import *
from src.static.fs import *


class SoundUI():

    def __init__(self, app):
        self.app = app
        self.ui:UIController = app.ui


    async def init(self):
        self.sound:SoundController = await self.app.enable_controller('sound')

    
    async def main_display(self):
        while True:
            response = await self.ui.display_choice_selector(
                    **UI_SOUND_MAIN_SELECTOR
                )
            if response['action'] == 'back_pressed':
                return
            selection = response['selected_option']['id']
            if selection==1:
                await self.play_predefined_sound()
            if selection==2:
                await self.play_custom_sound()
            if selection==3:
                await self.record_sound()


    async def play_predefined_sound(self):
        sound_names = self.sound.get_predefined_sounds()
        ui_data = [
                {'id':i, 'name': sound_name}
                for i, sound_name in enumerate(sound_names)
            ]
        response = await self.ui.display_choice_selector(
                **UI_SOUND_PLAY_PREDEFINED,
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return
        sound_name = response['selected_option']['name']
        await self.sound.play_sound(name=sound_name)


    async def play_custom_sound(self):
        try:
            files_list = list_files_in_folder(FS_SOUND_CUSTOM_FOLDER)
        except RayaFolderDoesNotExist:
            create_dat_folder(FS_SOUND_CUSTOM_FOLDER)
            files_list = []
        sounds_list = [
                file[:-4] 
                for file in files_list if file.endswith('.wav')
            ]
        if not sounds_list:
            await self.ui.display_action_screen(**UI_SOUND_NOT_CUSTOM_SOUNDS)
            return
        sounds_list.sort()
        ui_data = [
                {'id':i, 'name': sound_file_name}
                for i, sound_file_name in enumerate(sounds_list)
            ]
        response = await self.ui.display_choice_selector(
                **UI_SOUND_PLAY_PREDEFINED,
                data=ui_data,
            )
        if response['action'] == 'back_pressed':
            return
        sound_file_name = response['selected_option']['name']
        await self.sound.play_sound(
                path=f'{FS_SOUND_CUSTOM_FOLDER}/{sound_file_name}.wav'
            )


    async def record_sound(self):
        response = await self.ui.display_choice_selector(
                **UI_SOUND_RECORD_TIME_SELECTOR,
            )
        if response['action'] == 'back_pressed':
            return
        selection = response['selected_option']['id']
        if selection==0:
            response = await self.ui.display_input_modal(
                    **UI_SOUND_RECORD_TIME_INPUT
                )
            print(response)

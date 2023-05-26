import re
import asyncio

from raya.controllers.ui_controller import UIController
from raya.controllers.sound_controller import SoundController
from raya.tools.filesystem import delete_dat_file
from raya.exceptions import *

from src.tools.ui import ui_countdown, ui_list_of_files
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
            if selection==4:
                await self.play_recording()
            if selection==5:
                await self.delete_recording()


    async def play_predefined_sound(self):
        # List available predefined sounds in the UI controller.
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
        # Play the selected one
        sound_name = response['selected_option']['name']
        await self.sound.play_sound(name=sound_name)


    async def play_custom_sound(self):
        # List available sounds
        action, _, sound_file_name = await ui_list_of_files(
                ui_controller=self.ui,
                path=FS_SOUND_CUSTOM_FOLDER,
                selector_screen=UI_SOUND_PLAY_PREDEFINED,
                empty_screen=UI_SOUND_NOT_CUSTOM_SOUNDS,
                extension='.wav',
            )
        if action in ('back_pressed', 'empty'):
            return
        # Play the selected one.
        await self.sound.play_sound(
                path=f'{FS_SOUND_CUSTOM_FOLDER}/{sound_file_name}.wav'
            )


    async def actually_play_recorded_sound(self, recording_name):
        # Play a sound stored inside the folder FS_SOUND_RECORDINGS
        await self.ui.display_screen(
                **UI_SOUND_PLAYING_RECORDING,
                subtitle=f'Sound name: {recording_name}'
            )
        await self.sound.play_sound(
                path=f'{FS_SOUND_RECORDINGS}/{recording_name}.wav'
            )
        return


    async def record_sound(self):
        # Ask for the recording time.
        response = await self.ui.display_choice_selector(
                **UI_SOUND_RECORD_TIME_SELECTOR,
            )
        if response['action'] == 'back_pressed':
            return
        selection = response['selected_option']['id']
        if selection==0:
            time_to_record = None
            while time_to_record is None:
                response = await self.ui.display_input_modal(
                        **UI_SOUND_RECORD_TIME_INPUT
                    )
                if response['action'] in ('canceled', 'closed'):
                    return 
                try:
                    time_to_record = float(response['value'])
                except ValueError:
                    await self.ui.display_modal(**UI_ERROR_MUST_BE_NUMBER)
        else:
            time_to_record = float(response['selected_option']['id'])
        # Ask for the name of the recording
        response = await self.ui.display_input_modal(
                **UI_SOUND_RECORD_NAME_INPUT
            )
        if response['action'] in ('canceled', 'closed'):
            return 
        recording_name = str(response['value'])
        # Add the .wav extension if missing
        if not recording_name.endswith('.wav'):
            file_name = f'{recording_name}.wav'
        else:
            file_name = recording_name
        # Leave only alphanumeric, '.' and '_'
        file_name = re.sub(r"[^\w._]", "", file_name)
        # Launch a UI countdown as background task
        self.app.create_task(
                name='ui_countdown',
                afunc=ui_countdown,
                **UI_SOUND_RECORDING,
                ui_controller=self.ui,
                time=time_to_record,
            )
        # Record and save in FS_SOUND_RECORDINGS
        file_name = f'{FS_SOUND_RECORDINGS}/{file_name}'
        await self.sound.record_sound(
                duration=time_to_record,
                path=file_name,
                wait=True,
            )
        # Waits for the countdown task to finish
        try:
            await self.app.wait_for_task('ui_countdown')
        except RayaTaskNotRunning:
            pass
        # Ask if want to play the recording
        response = await self.ui.display_modal(**UI_ASK_PLAY_RECORDING)
        if response['action'] in ('canceled', 'closed'):
            return
        # Play the recorded audio
        await self.actually_play_recorded_sound(recording_name)
    

    async def play_recording(self):
        # List available sounds
        action, _, recording_name = await ui_list_of_files(
                ui_controller=self.ui,
                path=FS_SOUND_RECORDINGS,
                selector_screen=UI_SOUND_PLAY_RECORDING,
                empty_screen=UI_SOUND_NOT_RECORDINGS,
                extension='.wav',
            )
        if action in ('back_pressed', 'empty'):
            return
        # Play the selected one.
        await self.actually_play_recorded_sound(recording_name)


    async def delete_recording(self):
        # List available sounds
        action, _, recording_name = await ui_list_of_files(
                ui_controller=self.ui,
                path=FS_SOUND_RECORDINGS,
                selector_screen=UI_SOUND_DELETE_RECORDING,
                empty_screen=UI_SOUND_NOT_RECORDINGS,
                extension='.wav',
            )
        if action in ('back_pressed', 'empty'):
            return
        # Ask if actually want to delete
        response = await self.ui.display_modal(
                **UI_ASK_DELETE_RECORDING,
                content=(
                        'Sure you want to delete the recording '
                        f'\'{recording_name}\''
                    )
            )
        if response['action'] in ('canceled', 'closed'):
            return
        # Delete recording
        delete_dat_file(f'{FS_SOUND_RECORDINGS}/{recording_name}.wav')

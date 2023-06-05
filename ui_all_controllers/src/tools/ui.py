import asyncio
import math
import copy

from raya.controllers.ui_controller import UIController
from raya.tools.filesystem import list_files_in_folder, create_dat_folder
from raya.exceptions import *

async def ui_countdown(
            ui_controller:UIController,
            time:float,
            title:str
        ):
    iterations = int(math.floor(time))
    first_sleep = time - iterations
    await ui_controller.display_screen(
            title=title,
            subtitle=f'Time Remaining: -',
        )
    await asyncio.sleep(first_sleep)
    for i in range(iterations):
        await ui_controller.display_screen(
                title=title,
                subtitle=f'Time Remaining: {iterations-i}',
            )
        await asyncio.sleep(1.0)


async def ui_list_of_files(
            ui_controller:UIController,
            path:str,
            selector_screen:dict,
            empty_screen:dict,
            extension:str='',
            show_extension:bool=False,
            create_folder:bool=True,
            sort:bool=True,
        ):
    try:
        # Get all the files in the folder.
        files_list = list_files_in_folder(path)
    except RayaFolderDoesNotExist:
        if create_folder:
            create_dat_folder(path)
        files_list = []
    if extension:
        if extension.startswith('.'):
            extension = extension[1:]
        # Filter only the files with the extension
        files_list = [
                file if show_extension else file[:-4]
                for file in files_list if file.endswith(f'.{extension}')
            ]
    if not files_list:
        # If not files, show corresponding message and return.
        await ui_controller.display_action_screen(**empty_screen)
        return ('empty', None, None)
    # Show the list of files
    if sort:
        files_list.sort()
    ui_data = [
            {'id':i, 'name': sound_file_name}
            for i, sound_file_name in enumerate(files_list)
        ]
    response = await ui_controller.display_choice_selector(
            **selector_screen,
            data=ui_data,
        )
    if response['selected_option'] is None:
        return (response['action'], None, None)
    else:
        return (
                response['action'], 
                response['selected_option']['id'],
                response['selected_option']['name']
            )


def replace_key(template, **kargs):
    ui_return = copy.deepcopy(template)
    if 'title' in ui_return:
        for key, value in kargs.items():
            ui_return['title'] = ui_return['title'].replace(
                    f'{{{key}}}', value
                )
    if 'subtitle' in ui_return:
        for key, value in kargs.items():
            ui_return['subtitle'] = ui_return['subtitle'].replace(
                    f'{{{key}}}', value
                )
    return ui_return

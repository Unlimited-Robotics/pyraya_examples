import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'conference',
    'name': 'Conference',
}

UI_SCREEN = {
    'title':'Hello, Can I Help you?',
    'subtitle': 'Click below to call the fleet supervisor',
    'button_text': 'Start call',
    'loading_subtitle': 'Calling...',
    'call_on_join': False,
    **UI_COMMON_OPTIONS
}


class ConferenceComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        self.__running = True
        self.__call_to_action_pressed = False
        data_selector.append(self.select_button)


    async def run(self) -> typing.NoReturn:
        await self.app.ui.open_conference(
            wait=False,
            callback=self._cb_ui_conference,
            **UI_SCREEN
        )
        while self.__running:
            # if self.__call_to_action_pressed:
            #     response = await self.app.ui.display_modal(
            #         title='The call to action button was pressed',
            #         subtitle= '',
            #         content= '',
            #         cancel_text='',
            #         submit_text='Okay',
            #         show_icon=True,
            #         wait=True,
            #     )
            #     if response['action'] == 'confirmed':
            #         self.__call_to_action_pressed = False
            #         await self.app.ui.show_last_animation()
            await self.app.sleep(1)

    
    def _cb_ui_conference(self, response) -> typing.NoReturn:
        self.app.log.debug(f'Animation response: {response}')

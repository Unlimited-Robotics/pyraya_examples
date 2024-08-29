import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'call_to_action',
    'name': 'Call to Action',
}

UI_SCREEN = {
    'title':'Hello, Can I Help you?',
    'subtitle': 'I am Gary, your delivery robot',
    'button_text': 'Take me to my room',
    **UI_COMMON_OPTIONS
}


class CallToActionComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)


    def __init(self) -> None:
        self.__running = True
        self.__call_to_action_pressed = False


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.display_action_screen(
            wait=False,
            callback=self._cb_ui_display_call_to_action,
            **UI_SCREEN
        )
        while self.__running:
            if self.__call_to_action_pressed:
                response = await self.app.ui.display_modal(
                    title='The call to action button was pressed',
                    subtitle= '',
                    content= '',
                    cancel_text='',
                    submit_text='Okay',
                    show_icon=True,
                    wait=True,
                )
                if response['action'] == 'confirmed':
                    self.__call_to_action_pressed = False
                    await self.app.ui.show_last_animation()
            await self.app.sleep(1)

    
    def _cb_ui_display_call_to_action(self, response) -> typing.NoReturn:
        self.app.log.debug(f'Animation response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        elif response['action'] == 'button_clicked' and \
                response['id'] == 'CallToAction':
            self.app.log.debug('Call to Action button pressed')
            self.__call_to_action_pressed = True
        else:
            self.app.log.debug('Unknown button pressed')

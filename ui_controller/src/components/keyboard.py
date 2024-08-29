import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'keyboard',
    'name': 'Keyboard',
}

UI_SCREEN = {
    'title':'Hi! please type your name',
    **UI_COMMON_OPTIONS
}


class KeyboardComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)


    def __init(self) -> None:
        self.__running = True
        self.__keyboard_input_flag = False
        self.__keyboard_input_data = dict()


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.keyboard(
            wait=False,
            callback=self._cb_ui_keyboard,
            **UI_SCREEN
        )
        while self.__running:
            if self.__keyboard_input_flag:
                response = await self.app.ui.display_modal(
                    title=f'You typed: \'{self.__keyboard_input_data}\'',
                    subtitle= '',
                    content= '',
                    cancel_text='',
                    submit_text='Okay',
                    show_icon=True,
                    wait=True,
                )
                if response['action'] == 'confirmed':
                    self.__keyboard_input_flag = False
                    await self.app.ui.show_last_animation()
            await self.app.sleep(1)

    
    def _cb_ui_keyboard(self, response) -> typing.NoReturn:
        self.app.log.debug(f'response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        elif response['action'] == 'button_clicked':
            self.__keyboard_input_flag = True
            self.__keyboard_input_data = response['value']
        else:
            self.app.log.debug('Unknown button pressed')

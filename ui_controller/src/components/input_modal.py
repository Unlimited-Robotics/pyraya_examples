import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from raya.enumerations import UI_INPUT_TYPE
from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'input_modal',
    'name': 'Input Modal',
}

UI_SCREEN = {
    'title' : 'Do you want to subscribe?',
    'subtitle' : 'Enter your email address',
    'input_type': UI_INPUT_TYPE.TEXT,
    'cancel_text' : 'Cancel',
    'submit_text' : 'Submit',
    'placeholder' : 'Email Address',
    **UI_COMMON_OPTIONS
}


class InputModalComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)


    def __init(self) -> None:
        self.__running = True
        self.__input_value = None

        
    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.display_input_modal(
            wait=False,
            callback=self._cb_ui_input_modal,
            **UI_SCREEN
        )
        while self.__running:
            if self.__input_value:
                response = await self.app.ui.display_modal(
                    title=f'The value you entered is: \'{self.__input_value}\'',
                    subtitle= '',
                    content= '',
                    cancel_text='',
                    submit_text='',
                    show_icon=True,
                    wait=True,
                )
                if response['action'] == 'confirmed':
                    self.__input_value = False
                await self.app.sleep(5)
                return
            await self.app.sleep(1)

    
    def _cb_ui_input_modal(self, response) -> typing.NoReturn:
        self.app.log.debug(f'response: {response}')
        if response['action'] == 'canceled':
            self.app.log.debug('Cancelled')
            self.__running = False
        elif response['action'] == 'confirmed':
            self.app.log.debug('Confirmed')
            self.__input_value = response['value']
        else:
            self.app.log.debug('Unknown button pressed')

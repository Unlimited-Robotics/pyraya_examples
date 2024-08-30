import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from raya.enumerations import UI_MODAL_TYPE, UI_MODAL_SIZE

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'modal',
    'name': 'Modal',
}

UI_SCREEN = {
    'modal_type': UI_MODAL_TYPE.INFO,
    'title':'Atention!',
    'subtitle':'This is a modal',
    'content': 'Here you can see the information related to the modal',
    'cancel_text': 'Cancel',
    'submit_text': 'Ok',
    'modal_size': UI_MODAL_SIZE.BIG,
    'show_icon': True,
    'theme': UI_COMMON_OPTIONS['theme'],
}


class ModalComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)
        

    def __init(self) -> None:
        self.__running = True


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.display_modal(
            wait=False,
            callback=self._cb_ui_modal,
            **UI_SCREEN
        )
        while self.__running:
            await self.app.sleep(1)

    
    def _cb_ui_modal(self, response) -> typing.NoReturn:
        self.app.log.debug(f'Response: {response}')
        if response['action'] == 'confirmed':
            self.app.log.debug('Confirmed button pressed')
            self.__running = False
        elif response['action'] == 'canceled':
            self.app.log.debug('Canceled button pressed')
            self.__running = False
        elif response['action'] == 'closed':
            self.app.log.debug('Modal closed')
            self.__running = False
        else:
            self.app.log.debug('Unknown button pressed')

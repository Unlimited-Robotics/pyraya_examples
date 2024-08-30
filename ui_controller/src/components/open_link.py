import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'open_link',
    'name': 'Open Link',
}

UI_SCREEN = {
    'title':'Hello! I\'m Gary, your delivery robot',
    'url': 'https://www.unlimited-robotics.com/',
    **UI_COMMON_OPTIONS
}


class OpenLinkComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)
        

    def __init(self) -> None:
        self.__running = True


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.open_link(
            wait=False,
            callback=self._cb_ui_url,
            **UI_SCREEN
        )
        while self.__running:
            await self.app.sleep(1)

    
    def _cb_ui_url(self, response) -> typing.NoReturn:
        self.app.log.debug(f'response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        else:
            self.app.log.debug('Unknown button pressed')

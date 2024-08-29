import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'interacty',
    'name': 'Interacty',
}

UI_SCREEN = {
    'title':'This is the Interacty Component',
    'hash': 'hjdxihmrmvzfg28z99t24a-p6o2-sog',
    **UI_COMMON_OPTIONS
}


class InteractyComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)
        

    def __init(self) -> None:
        self.__running = True


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.open_interacty(
            wait=False,
            callback=self._cb_ui_show_animation,
            **UI_SCREEN
        )
        while self.__running:
            await self.app.sleep(1)

    
    def _cb_ui_show_animation(self, response) -> typing.NoReturn:
        self.app.log.debug(f'Animation response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        else:
            self.app.log.debug('Unknown button pressed')

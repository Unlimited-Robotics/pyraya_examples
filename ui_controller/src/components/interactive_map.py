import typing
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'interactive_map',
    'name': 'Interactive Map',
}

UI_SCREEN = {
    'title':'Gary is at the Entrance!!',
    'subtitle': 'You can click in the map to move Gary trough the map',
    'map_name': 'Main__1',
    'show_robot_position': True,
    'view_only': False,
    **UI_COMMON_OPTIONS
}


class InteractiveMapComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)


    def __init(self) -> None:
        self.__running = True
        self.__navigate_pressed = False
        self.__navigation_data = dict()


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.display_interactive_map(
            wait=False,
            callback=self._cb_ui_interactive_map,
            **UI_SCREEN
        )
        while self.__running:
            if self.__navigate_pressed:
                response = await self.app.ui.display_modal(
                    title=f'The coordinates are {self.__navigation_data}',
                    subtitle= '',
                    content= '',
                    cancel_text='',
                    submit_text='Okay',
                    show_icon=True,
                    wait=True,
                )
                if response['action'] == 'confirmed':
                    self.__navigate_pressed = False
                    await self.app.ui.show_last_animation()
            await self.app.sleep(1)

    
    def _cb_ui_interactive_map(self, response) -> typing.NoReturn:
        self.app.log.debug(f'response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        elif response['action'] == 'navigate':
            self.__navigate_pressed = True
            self.__navigation_data = response['coordinates']
        else:
            self.app.log.debug('Unknown button pressed')

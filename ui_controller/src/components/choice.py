import typing
import base64
if typing.TYPE_CHECKING:
    from ..app import RayaApplication

from raya.utils.internal_filesystem import resolve_path

from ..constants import UI_COMMON_OPTIONS

SELECTOR = {
    'id': 'choice',
    'name': 'Choice',
}

DATA_CHOICE = [
  {
    'id': 1,
    'name': 'Bottle',
    'imgSrc': 'res:bottle.png',
  },
  {
    'id': 2,
    'name': 'Cup',
    'imgSrc': 'res:cup.png',
  }
]

UI_SCREEN = {
    'title':'Please select an option',
    'data': DATA_CHOICE,
    **UI_COMMON_OPTIONS
}


class ChoiceComponent:
    
    def __init__(self, app: 'RayaApplication', data_selector: list):
        self.app = app
        self.select_button = SELECTOR
        data_selector.append(self.select_button)
        for data in DATA_CHOICE:
            data['imgSrc'] = self.convert_image_to_base64(data['imgSrc'])


    def __init(self) -> None:
        self.__running = True
        self.__choice_pressed = False
        self.__selected_choice = ''


    def convert_image_to_base64(self, image_path) -> str:
        image_path = resolve_path(image_path)
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        image = encoded_string.decode('utf-8')
        return f'data:image/png;base64,{image}'


    async def run(self) -> typing.NoReturn:
        self.__init()
        await self.app.ui.display_choice_selector(
            wait=False,
            callback=self._cb_ui_display_choice,
            **UI_SCREEN
        )
        while self.__running:
            if self.__choice_pressed:
                response = await self.app.ui.display_modal(
                    title=f'\'{self.__selected_choice}\' was selected!',
                    subtitle= '',
                    content= '',
                    cancel_text='',
                    submit_text='Okay',
                    show_icon=True,
                    wait=True,
                )
                if response['action'] == 'confirmed':
                    self.__choice_pressed = False
                    await self.app.ui.show_last_animation()
            await self.app.sleep(1)

    
    def _cb_ui_display_choice(self, response) -> typing.NoReturn:
        # self.app.log.debug(f'Animation response: {response}')
        if response['action'] == 'back_pressed':
            self.app.log.debug('Back button pressed')
            self.__running = False
        elif response['action'] == 'item_selected':
            self.__choice_pressed = True
            self.__selected_choice = response['selected_option']['name']
        else:
            self.app.log.debug('Unknown button pressed')

from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController
from raya.enumerations import *

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        # Create local attributes and variables
        self.ui: UIController = await self.enable_controller('ui')
        self.games_feedback = None

    async def loop(self):
        await self.ui.open_memory_game(difficulty = 'Easy',
            back_button_text = '',
            theme = UI_THEME_TYPE.WHITE,
            wait = False,
            async_callback_feedback = self.async_cb_fd,
            async_callback_finish = self.async_cb_finish,
        )
        self.log.info('Memory game opened')
        while True:
            await self.sleep(1)

    
    # Async feedback for games
    async def async_cb_fd(self, fb):
        self.log.debug(f'GAMES Feedback: {fb}')
        
    async def async_cb_finish(self, fb):
        self.log.debug(f'GAMES Finish: {fb}')
        self.finish_app()

    async def finish_app(self):
        self.log.info('Memory game close')

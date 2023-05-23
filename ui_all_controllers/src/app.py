from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController

from src.static.ui import *
from src.controllers_ui.sound_ui import SoundUI

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        # Controllers
        self.ui:UIController = await self.enable_controller('ui')
        # UI Controllers Handlers
        self.handlers = {
            1: SoundUI(self)
        }
        for handler in self.handlers.values():
            await handler.init()


    async def loop(self):
        # Loop
        selection = (await self.ui.display_choice_selector(
                **UI_CONTROLLER_SELECTOR
            ))['selected_option']['id']
        
        if selection in self.handlers:
            await self.handlers[selection].main_display()
        else:
            self.finish_app()


    async def finish(self):
        await self.ui.display_screen(**UI_SCREEN_END)

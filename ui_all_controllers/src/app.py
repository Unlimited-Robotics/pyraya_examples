from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController
from raya.exceptions import RayaException

from src.static.ui.general import *
from src.controllers_ui.sound_ui import SoundUI
from src.controllers_ui.arms_ui import ArmsUI

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        # Controllers
        self.ui:UIController = await self.enable_controller('ui')
        # UI Controllers Handlers
        self.handlers = {
            1: SoundUI(self),
            2: ArmsUI(self),
        }
        for handler in self.handlers.values():
            await handler.init()


    async def loop(self):
        # Loop
        try:
            # Ask for the controller to test
            response = await self.ui.display_choice_selector(
                    **UI_CONTROLLER_SELECTOR
                )
            if response['action'] == 'back_pressed':
                self.finish_app()
            selection = response['selected_option']['id']
            if selection in self.handlers:
                await self.handlers[selection].main_display()
            else:
                self.finish_app()
        except RayaException as e:
            # If a Ra-Ya exception is raised, show it as a UI modal.
            # TODO: Add multiline in content when it gets implemented
            # to separate file and exception text.
            error_file, error_lineno = e.get_raya_file()
            await self.ui.display_modal(
                    **UI_RAYA_EXCEPTION,
                    subtitle=type(e).__name__,
                    content=f'{error_file}[{error_lineno}]: {str(e)}',
                )


    async def finish(self):
        await self.ui.display_screen(**UI_END)

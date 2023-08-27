from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController
from raya.exceptions import RayaException

from src.static.ui.general import *
from src.handlers.sound_handler import SoundHandler
from src.handlers.arms_handler import ArmsHandler
from src.handlers.motion_handler import MotionHandler
from src.handlers.leds_handler import LedsHandler


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        # Controllers
        self.ui:UIController = await self.enable_controller('ui')
        # UI Controllers Handlers
        self.handlers = {
            1: SoundHandler(self),
            2: ArmsHandler(self),
            3: MotionHandler(self),
            4: LedsHandler(self),
        }
        for handler in self.handlers.values():
            await handler.init()


    async def loop(self):
        # Loop
        try:
            if self.selection == -1:
                # Ask for the controller to test
                response = await self.ui.display_choice_selector(
                        **UI_CONTROLLER_SELECTOR
                    )
                if response['action'] == 'back_pressed':
                    self.finish_app()
                selection = response['selected_option']['id']
            else:
                selection = self.selection
            if selection in self.handlers:
                await self.handlers[selection].main_display(self.sub_selection)
            else:
                self.finish_app()
        except RayaException as e:
            # If a Ra-Ya exception is raised, show it as a UI modal.
            # TODO: Add multiline in content when it gets implemented
            # to separate file and exception text.
            error_file, error_lineno = e.get_raya_file()
            await self.ui.display_modal(
                    **UI_RAYA_EXCEPTION,
                    subtitle='Something happened',
                    #subtitle=type(e).__name__,
                    content=f'{error_file}[{error_lineno}]: {str(e)}',
                )


    async def finish(self):
        await self.ui.display_screen(**UI_END)


    def get_arguments(self):
        self.selection = self.get_argument(
                '--selection1',
                type=int,
                required=False,
                default=-1,
            )
        self.sub_selection = self.get_argument(
                '--selection2',
                type=int,
                required=False,
                default=-1,
            )

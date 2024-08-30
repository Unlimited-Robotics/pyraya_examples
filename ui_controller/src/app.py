import copy

from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController

from .constants import *
from .components import AnimationComponent, CallToActionComponent
from .components import ChoiceComponent, ConferenceComponent
from .components import DisplayScreenComponent, InputModalComponent
from .components import InteractiveMapComponent, InteractyComponent
from .components import KeyboardComponent, ModalComponent
from .components import OpenLinkComponent, OpenVideoComponent
from .constants import UI_COMMON_OPTIONS

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.ui: UIController = await self.enable_controller('ui')
        self.data = [
            {
                'id': 'finish',
                'name': 'Finish App',
            }
        ]
        
        self.animation = AnimationComponent(
            app=self, 
            data_selector=self.data
        )
        self.call_to_action = CallToActionComponent(
            app=self, 
            data_selector=self.data
        )
        self.choice = ChoiceComponent(
            app=self, 
            data_selector=self.data
        )
        self.conference = ConferenceComponent(
            app=self, 
            data_selector=self.data
        )
        self.display_screen = DisplayScreenComponent(
            app=self, 
            data_selector=self.data
        )
        self.input_modal = InputModalComponent(
            app=self, 
            data_selector=self.data
        )
        self.interactive_map = InteractiveMapComponent(
            app=self, 
            data_selector=self.data
        )
        self.interacty = InteractyComponent(
            app=self, 
            data_selector=self.data
        )
        self.keyboard = KeyboardComponent(
            app=self, 
            data_selector=self.data
        )
        self.modal = ModalComponent(
            app=self, 
            data_selector=self.data
        )
        self.open_link = OpenLinkComponent(
            app=self, 
            data_selector=self.data
        )
        self.open_video = OpenVideoComponent(
            app=self, 
            data_selector=self.data
        )
        
        self.actions = {
            self.animation.select_button['id']: self.animation,
            self.call_to_action.select_button['id']: self.call_to_action,
            self.choice.select_button['id']: self.choice,
            self.conference.select_button['id']: self.conference,
            self.display_screen.select_button['id']: self.display_screen,
            self.input_modal.select_button['id']: self.input_modal,
            self.interactive_map.select_button['id']: self.interactive_map,
            self.interacty.select_button['id']: self.interacty,
            self.keyboard.select_button['id']: self.keyboard,
            self.modal.select_button['id']: self.modal,
            self.open_link.select_button['id']: self.open_link,
            self.open_video.select_button['id']: self.open_video,
        }
        self.main_ui_options = copy.deepcopy(UI_COMMON_OPTIONS)
        self.main_ui_options['back_button_text'] = ''


    async def loop(self):
        
        response = await self.ui.display_choice_selector(
            title='Main Menu',
            data=self.data,
            max_items_shown=4,
            wait=True,
            **self.main_ui_options
        )
        self.log.debug(f'Selected: {response}')
        if 'selected_option' not in response or response['selected_option'] is None:
            return
        
        if response['selected_option']['id'] == 'finish':
            await self.finish_app()
        else:
            selected_id = response['selected_option']['id']
            if selected_id in self.actions:
                await self.actions[selected_id].run()


    async def finish(self):
        self.log.info('App finished')

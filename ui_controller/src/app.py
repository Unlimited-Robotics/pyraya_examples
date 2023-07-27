from raya.application_base import RayaApplicationBase
from raya.enumerations import UI_MODAL_TYPE, UI_THEME_TYPE
from raya.controllers.ui_controller import UIController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.UI: UIController = await self.enable_controller('ui')


    async def loop(self):
        await self.UI.display_screen(
                title='Welcome!',
                subtitle='Good morning',
                languages=['he', 'en', 'ru'],
                chosen_language='ru',
                theme=UI_THEME_TYPE.DARK
            )
        await self.sleep(5)
        res = await self.UI.display_modal(
                title='This is a modal',
                submit_text='OK',
                subtitle='',
                show_icon=False,
                cancel_text='Go back home',
                wait=True,
            )
        self.log.info(f'res = {res}')
        await self.sleep(1)

        data = [{
                'id': 1,
                'name': 'Martin'
            }, {
                'id': 2,
                'name': 'Gary'
            }, {
                'id': 3,
                'name': 'Nitsan'
            }]
        response = await self.UI.display_choice_selector(
                title='What is my name?',
                show_back_button=False,
                data=data
            )

        if response['selected_option']['id'] == 2:
            subtitle = 'That is correct! Want to close the app?'
            modal_type = UI_MODAL_TYPE.SUCCESS
        else:
            subtitle = 'That\'s wrong!  Want to close the app?'
            modal_type = UI_MODAL_TYPE.ERROR

        response = await self.UI.display_modal(
                title='Modal',
                subtitle=subtitle,
                modal_type=modal_type
            )

        if response['action'] == 'confirmed':
            self.finish_app()


    async def finish(self):
        self.log.info('App finished')

from raya.application_base import RayaApplicationBase
from raya.controllers.ui_controller import UIController


IMAGEN_MARINE_PATH = 'res:animal.jpeg'
IMAGE_BRIDGE_SRC = 'https://www.w3schools.com/howto/img_forest.jpg'
IMAGE_ARROW_PATH = 'res:arrow1.json'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.UI: UIController = await self.enable_controller('ui')
        self.log.info(f'Hello from setup()')


    async def loop(self):
        # Welcome screen
        await self.UI.display_screen(
                title='Hi there!',
                subtitle='Look at this!'
            )
        await self.sleep(1)
        
        # URL image
        self.log.info(f'Displaying {IMAGE_BRIDGE_SRC} URL animation')
        await self.UI.show_animation(
            title = 'This is a bridge with a forest',
            subtitle='This a image from a URL',
            url = IMAGE_BRIDGE_SRC
        )
        await self.sleep(5)
        
        # Lottie File
        self.log.info(f'Displaying {IMAGE_ARROW_PATH} animation')
        await self.UI.show_animation(
            title = 'This is a bridge with a forest',
            subtitle='This a lottie file',
            lottie = IMAGE_ARROW_PATH
        )
        await self.sleep(5)
        
        #Image from path
        self.log.info(f'Displaying {IMAGEN_MARINE_PATH} animation')
        await self.UI.show_animation(
                title = 'This is Spirobranchus giganteus',
                subtitle='This is a Jpeg file',
                path = IMAGEN_MARINE_PATH
            )
        await self.sleep(5)
        self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')

import base64
import json

from raya.application_base import RayaApplicationBase
from raya.enumerations import ANIMATION_TYPE
from raya.controllers.ui_controller import UIController
from raya.tools.filesystem import open_file


IMAGEN_MARINE_PATH = 'res:animal.jpeg'
IMAGE_BRIDGE_SRC = 'https://www.w3schools.com/howto/img_forest.jpg'
IMAGE_ARROW_PATH = 'res:arrow1.json'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.UI: UIController = await self.enable_controller('ui')
        self.log.info(f'Hello from setup()')


    async def loop(self):
        arrow_anim = json.load(open_file(IMAGE_ARROW_PATH))
        with open_file(IMAGEN_MARINE_PATH, 'rb') as f:
            marine_anim = base64.b64encode(f.read()).decode('utf-8')

        await self.UI.display_screen(
                title='Hi there!',
                subtitle='Look at this!'
            )
        await self.sleep(1)

        self.log.info(f'Displaying {IMAGE_ARROW_PATH} animation')
        await self.UI.display_animation(
                title = 'Go there',
                subtitle='This is a Lottie file',
                content = arrow_anim, format=ANIMATION_TYPE.LOTTIE
            )
        await self.sleep(5)

        # URL image
        self.log.info(f'Displaying {IMAGE_BRIDGE_SRC} URL animation\n')
        await self.UI.display_animation(
                title = 'This is a bridge with a forest',
                subtitle='This a Jpeg file',
                content = IMAGE_BRIDGE_SRC, format=ANIMATION_TYPE.URL
            )
        await self.sleep(5)

        #base64 image
        self.log.info(f'Displaying {IMAGEN_MARINE_PATH} animation')
        await self.UI.display_animation(
                title = 'This is Spirobranchus giganteus',
                subtitle='This is a Jpeg file',
                content = marine_anim, format=ANIMATION_TYPE.JPEG
            )
        await self.sleep(5)
        self.finish_app()


    async def finish(self):
        self.log.warn(f'Hello from finish()')

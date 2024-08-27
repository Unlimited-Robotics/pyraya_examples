
from raya.application_base import RayaApplicationBase
from raya.controllers import SoundController
from raya.controllers import LedsController
from raya.controllers import UIController

from raya.enumerations import LEDS_EXECUTION_CONTROL


LEDS_GARY_SPEAKING = {
    'group': 'head',
    'color': 'CYAN',
    'animation': 'MOTION_4',
    'speed': 6,
    'execution_control': LEDS_EXECUTION_CONTROL.OVERRIDE, 
}


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.sound: SoundController = await self.enable_controller('sound')
        self.leds: LedsController = await self.enable_controller('leds')
        self.ui: UIController = await self.enable_controller('ui')


    async def main(self):

        self.log.info('BEFORE')
        await self.ui.display_screen(title='Speaking...')
        await self.leds.animation(**LEDS_GARY_SPEAKING, wait=False)
        await self.sound.play_sound(name='VOICE_FAILED_ATTACH_ENGLISH')
        self.log.info('AFTER')


    async def finish(self):
        pass

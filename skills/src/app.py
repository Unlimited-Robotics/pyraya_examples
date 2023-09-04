import asyncio

from raya.controllers.motion_controller import MotionController
from raya.application_base import RayaApplicationBase

from skills.motion_skills.rotate_too_much import SkillRotateTooMuch


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Setup from App')
        self.ctlr_motion:MotionController = \
                await self.get_controller('motion')
        self.skill_toorotate = self.register_skill(SkillRotateTooMuch)


    async def main(self):
        self.log.info('Run from App')
        await self.skill_toorotate.run()


    async def finish(self):
        self.log.info('Finish from App')

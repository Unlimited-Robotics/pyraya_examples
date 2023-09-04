from raya.controllers.motion_controller import MotionController
from raya.skill import RayaSkill


class SkillRotateTooMuch(RayaSkill):

    async def setup(self):
        self.ctlr_motion:MotionController = \
                await self.get_controller('motion')
        pass


    async def run(self):
        await self.ctlr_motion.rotate(
                angle=45,
                angular_speed=20,
                wait=True
            )


    async def finish(self):
        pass

from raya.controllers.motion_controller import MotionController
from raya.skills.skill import RayaSkill


class SkillRotateTooMuch(RayaSkill):

    async def setup(self):
        self.ctlr_motion:MotionController = \
                await self.get_controller('motion')


    async def main(self):
        await self.ctlr_motion.rotate(
                angle=20,
                angular_speed=40,
                wait=True
            )


    async def finish(self):
        pass

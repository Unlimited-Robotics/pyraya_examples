from raya.application_base import RayaApplicationBase

from skills.connect_to_cart import SkillConnectToCart


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Setup from App')
        self.skill_connect = self.register_skill(SkillConnectToCart)


    async def main(self):
        self.log.info('Run from App')
        await self.skill_connect.run()


    async def finish(self):
        self.log.info('Finish from App')

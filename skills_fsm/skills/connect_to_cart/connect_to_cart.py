from raya.skills import RayaSkill, RayaSkillHandler

from skills.approach_to_tags import SkillApproachToTags


class SkillConnectToCart(RayaSkill):

    async def setup(self):
        self.skill_apr2tags:RayaSkillHandler = \
                self.register_skill(SkillApproachToTags)


    async def main(self):
        print('A')
        await self.skill_apr2tags.run(
                setup_args={
                        'working_camera': 'chest',
                        'identifier': [1, 2],
                        'tags_size': 0.08,
                    }
            )
        print('B')


    async def finish(self):
        pass

# System Imports 

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')        

        self.log.info(f'Clean arms status started...')
        await self.manip.clean_arms_status(self.arms)
        

    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.arms = self.get_argument(
                '-a', '--arms', 
                type=str, 
                default=[],
                nargs='+', 
                help='list of arms'
            )

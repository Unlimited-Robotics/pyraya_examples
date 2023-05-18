# System Imports

# Raya imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')        

        await self.manip.place_object_with_point(
                point_to_place=self.point, 
                arm=self.arm,
                callback_feedback=self.cb_manipulation_feedback,
                wait=True,
            )
        self.log.info('Place Object with point started...')
    

    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.point = self.get_argument(
                '-p', '--point-to-place',
                type=float,
                list=True,
                default=[0.5, -0.02, 0.7],
                help='list of floats with the point'
            )
        self.arm = self.get_argument(
                '-a', '--arm', 
                type=str, 
                required=True, 
                help='arm to place'
            )


    def cb_manipulation_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')

# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')  
              
        if self.pick_height > self.object_height:
            self.log.error('pick height cant be bigger than object height')
            self.finish_app()

        


    async def loop(self):

        self.log.info(f'Pick Object Point started...')
        await self.manip.pick_object_point(point = self.point,
                object_height=self.object_height, 
                pick_height=self.pick_height, 
                pressure=self.pressure,
                width=self.width, 
                angles=self.angles,
                arms=self.arms,
                method='angles_rotation',
                callback_feedback=self.cb_manipulation_feedback,
                wait=True
            )
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.point = self.get_argument(
                '-pp', '--point-to-pick',
                type=float,
                required=True,
                list= True, 
                help='list of floats with the point'
            )
        self.angles = self.get_argument(
                '-g', '--angles',
                type=int,
                list=True,
                default=[-90, 90, 30],
                help=(
                        'Angles to check pick in degrees: ' 
                        'initial_angle final_angle steps. eg 0 90 10t'
                    )
            )
        self.object_height = self.get_argument(
                '-oh', '--object-height',
                type=float,
                required=True, 
                help='object height in meters'
            )
        self.arms = self.get_argument(
               '-a', '--arms',
               type=str, 
               default=[],
               list= True, 
               help='list of arms to try to pick'
            )
        self.width = self.get_argument(
                '-w', '--width',
                type=float,
                required=True, 
                help='object width in meters'
            )
        self.pressure = self.get_argument(
                '-pr', '--pressure',
                type=float,
                required=False, 
                default=0.5, 
                help='gripper pressure'
            )
        self.pick_height = self.get_argument(
                '-ph', '--pick-height',
                type=float, 
                required=True, 
                help='height user want to pick the object'
            )
        


    def cb_manipulation_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')

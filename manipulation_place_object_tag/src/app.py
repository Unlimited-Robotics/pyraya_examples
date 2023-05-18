# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')        

        await self.manip.place_object_with_tag(
                tag_family=self.tag_family, 
                tag_id=self.tag_id, 
                source=self.camera,
                tag_size=self.tag_size,
                arm=self.arm,
                callback_feedback=self.cb_manipulation_feedback,
                wait=True,
            )
        self.log.info(f'Place Object with tag started...')
    

    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.tag_family = self.get_argument(
                '-tf', '--tag-family',
                type=str, 
                required=True,
                default='tag36h11', 
                help='tag family'
            )
        self.tag_id = self.get_argument(
               '-ti', '--tag-id',
               type=int,
               required=True, 
               default='tag36h11', 
               help='tag id'
            )
        self.tag_size = self.get_argument(
                '-ts', '--tag-size',
                type=float, 
                required=True, 
                help='Size of tag in meters'
            )
        self.camera = self.get_argument(
                '-c', '--camera', 
                type=str, 
                required=False, 
                help='camera to detect tag'
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

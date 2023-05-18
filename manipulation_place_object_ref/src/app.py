# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')        

        await self.manip.place_object_with_reference(
                detector_model=self.model, 
                source=self.camera, 
                object_name=self.object_ref, 
                distance=self.distance,
                arm=self.arm,
                callback_feedback=self.cb_manipulation_feedback,
                wait=True
            )
        self.log.info(f'Place Object started...')
 

    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='yolov5s_coco',
                help='object detector model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True, 
                help='name of camera to use'
            )
        self.object_ref = self.get_argument(
                '-o', '--object-reference',
                type=str, 
                default='cup', 
                help='object reference to place'
            )
        self.distance = self.get_argument(
               '-d', '--distance',
               type=float, 
               default='0.1', 
               help='Distance in meters to put it from reference object'
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

# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.manipulation_controller import ManipulationController


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.manip:ManipulationController = \
                await self.enable_controller('manipulation')        

        await self.manip.pick_object(detector_model = self.model, 
                source=self.camera, 
                object_name=self.object, 
                arms=self.arms,
                method=self.method,
                pressure=self.pressure,
                timeout=self.timeout,
                callback_feedback=self.cb_manipulation_feedback,
                wait=True,
            )
        self.log.info(f'Pick Object started...')


    async def loop(self):
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='yolov5s_coco',
                help='object model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True, 
                help='name of camera to use'
            )
        self.object = self.get_argument(
                '-o', '--object-name',
                type=str, 
                default='bottle', 
                help='object to pick'
            )
        self.arms = self.get_argument(
               '-a', '--arms',
               type=list, 
               default=[],
               nargs='+', 
               help='list of arms to try to pick'
            )
        self.method = self.get_argument(
                '-md', '--method',
                type=str, 
                default='', 
                help='method to use'
            )
        self.pressure = self.get_argument(
                '-pr', '--pressure',
                type=float,
                required=False, 
                default=0.5, 
                help='gripper pressure'
            )
        self.timeout = self.get_argument(
                '-t', '--timeout',
                type=float,
                required=False, 
                default=0.0, 
                help='time to wait detections'
            )


    def cb_manipulation_feedback(self, feedback_code, feedback_msg):
        self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')

# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cv_controller import CVController


class RayaApplication(RayaApplicationBase):

    async def setup(self): 
        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')


    async def loop(self):
        self.log.info(f'Deleting faces: {self.names} ...')
        faces_deleted, faces_not_deleted = \
            await self.cv.delete_face(
                    faces_to_delete=self.names,
                    model_name=self.model
                )
        self.log.info(f'Faces Deleted: {faces_deleted}')
        self.log.info(f'Faces Not Deleted: {faces_not_deleted}')
        self.finish_app()


    async def finish(self):
        self.log.info('Finish app called')


    def get_arguments(self):
        self.names = self.get_argument(
                '-n', '--names', 
                required=True,
                nargs='+', 
                help=(
                    'list with the names of faces to delete'
                )
            )
        self.model = self.get_argument(
                '-m',  '--model', 
                default='deepknn_face',
                help='face recognition model name'
            )

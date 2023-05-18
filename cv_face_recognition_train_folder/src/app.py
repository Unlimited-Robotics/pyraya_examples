# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cv_controller import CVController
from raya.tools.filesystem import download_file, check_folder_exists


DEFAULT_FOLDER_URL = (
        'https://storage.googleapis.com/raya_files/Common/data_examples/' 
        'faces_train.tar.gz'
    )


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info((
                'Ra-Ya Py - Computer vision Face train example'
                ' with folder as input'
            ))

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.log.info('Training face recognition model...')

        # Enable detector
        model_params = {}

        # Check if model exists in data folder, if not download it
        folder_path = f'dat:{self.data_path}/'
        if not check_folder_exists(folder_path):
            self.log.info('Downloading model folder...')
            download_file(
                    url=DEFAULT_FOLDER_URL,
                    folder_path=folder_path, 
                    extract=True
                )
        self.log.info('Training...')
        # Launch train model folder command
        self.recognizer = await self.cv.train_model_folder_path(
                model_name = self.model,
                data_path = str(folder_path),
                model_params = model_params
            )
        faces = self.recognizer['faces']
        self.log.info(f'Faces trained: {faces}')
        self.log.info('Trained finished')
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='deepknn_face',
                help='face model name'
            )
        self.data_path = self.get_argument(
                '-d', '--data_path',
                default= 'faces_train',
                help='path with the images to train the faces',
            )
        
# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController
import time

CAMERA = 'nav_bottom'
DELAY = 0.3
PREDICTION_TIMEOUT = 5.0
MODEL_NAME = 'apriltags'



class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision')
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        await self.cameras.enable_camera(CAMERA)
        self.cv: CVController = await self.enable_controller('cv')
        self.model_params = {}
        self.prediction_received = False
        self.tries = 0


    async def loop(self):
        self.tries += 1
        self.log.info('')
        self.log.info(f'Enabling model, try {self.tries}...')
        start_time = time.time()
        self.model= await self.cv.enable_model(
                name=MODEL_NAME, 
                source=CAMERA,
                model_params = self.model_params
            )
        print('ENABLING TIME: ', time.time()-start_time)
        class_type = type(self.model).__name__
        if class_type in ['ObjectsDetectorHandler', 
                          'FacesDetectorHandler',
                          'TagsDetectorHandler']:
            self.model.set_detections_callback(
                    callback=self.callback_all_prediction,
                    call_without_detections=True,
                )
        elif class_type == 'ObjectsSegmentatorHandler':
            self.model.set_segmentations_callback(
                    callback=self.callback_all_prediction,
                    call_without_segmentations=True,
                )       
        elif class_type == 'FacesRecognizerHandler':
            self.model.set_recognitions_callback(
                    callback=self.callback_all_prediction,
                    call_without_recognitions=True,
                )    
        elif class_type == 'ObjectsClassifierHandler':
            self.model.set_classifications_callback(
                    callback=self.callback_all_prediction,
                    call_without_classifications=True,
                )          
        self.log.info('Model enabled')
        await self.sleep(DELAY)
        self.log.info('Waiting for prediction...')
        counter = 0
        while not self.prediction_received:
            counter += 1
            if counter >= PREDICTION_TIMEOUT/0.1:
                self.log.error('Not prediction received')
                self.log.error(f'Timeout of {PREDICTION_TIMEOUT} reached')
                self.log.error(f'Failed at try {self.tries}')
                self.finish_app()
                return
            await self.sleep(0.1)
        self.log.info('Predictions received')
        self.prediction_received = False
        await self.sleep(DELAY)

        self.log.info('Disabling model...')
        start_time2 = time.time()
        await self.cv.disable_model(model_obj=self.model)
        self.log.info('Model disabled')
        print('DISABLING TIME: ', time.time()-start_time2)
        print('time enabling and disabling: ', time.time()-start_time)
        await self.sleep(1.0)

    
    def callback_all_prediction(self, _):
        self.prediction_received = True


    async def finish(self):
        self.log.info('')
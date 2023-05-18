# System Imports
import json

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cv_controller import CVController


class RayaApplication(RayaApplicationBase):
    
    async def setup(self):
        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')

        # Get Available models to run
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))


    async def loop(self):
        self.finish_app()
        

    async def finish(self):
        pass

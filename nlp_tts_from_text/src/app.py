# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.nlp_controller import NlpController



class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Tag Detection Example')
        self.nlp: NlpController = await self.enable_controller('nlp')
        await self.nlp.tts_set_provider(
                'google_tts'
            )


    async def loop(self):
        await self.nlp.tts_play_text(
                text='Hello this is a test', 
                voice='us',
                language='en',
                callback_feedback=self.cb_transcribe_feedback,
                wait=True,
            )
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def cb_transcribe_feedback(self, feedback_code, feedback_msg):
        # self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')
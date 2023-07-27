# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.nlp_controller import NlpController


CREDENTIALS_FILE = f'res:client_service_key.json'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Tag Detection Example')
        self.nlp: NlpController = await self.enable_controller('nlp')
        await self.nlp.stt_set_provider(
                'google_stt', 
                credentials_file=CREDENTIALS_FILE
            )


    async def loop(self):
        text = await self.nlp.stt_transcribe_from_mic(
                microphone='head', 
                voice_detector='silero_v4',
                language='en-US',
                timeout=5.0,
                callback_feedback=self.cb_transcribe_feedback,
                wait=True,
            )
        self.log.info(f'Result: {text}')
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def cb_transcribe_feedback(self, feedback_code, feedback_msg):
        # self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')
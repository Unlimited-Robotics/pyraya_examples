# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.nlp_controller import NLPController


CREDENTIALS_FILE = f'res:client_service_key.json'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(
                'Ra-Ya Py - Speech to text with microphone Detection Example'
            )
        self.nlp: NLPController = await self.enable_controller('nlp')
        await self.nlp.stt_set_provider(
                self.provider, 
                credentials_file=CREDENTIALS_FILE
            )


    async def loop(self):
        text = await self.nlp.stt_transcribe_from_mic(
                microphone=self.microphone, 
                voice_detector=self.voice_detector,
                language=self.language,
                timeout=self.timeout,
                callback_feedback=self.cb_transcribe_feedback,
                callback_finish=self.cb_transcribe_finish,
                wait=True,
            )
        self.log.info(f'Result: {text}')
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.provider = self.get_argument(
                '-p', '--provider', 
                default='google_stt',
                help='provider to use'
            )
        self.voice_detector = self.get_argument(
                '-v', '--voice-detector', 
                type=str, 
                default='silero_v4',
                help='voice detector to use with microphone'
            )
        self.microphone = self.get_argument(
                '-m', '--microphone', 
                type=str, 
                default='head',
                help='microphone name to use'
            )       
        self.language = self.get_argument(
                '-l', '--language', 
                type=str, 
                default='en-US',
                help='voice language, may change depending the provider'
            )   
        self.timeout = self.get_argument(
                '-t',  '--timeout', 
                type=float, 
                default=5.0,
                help='time to record, if not voice detector is setted'
            ) 
          

    def cb_transcribe_feedback(self, feedback_code, feedback_msg):
        # self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')


    def cb_transcribe_finish(self, error, error_msg, transcription):
        self.log.info(f'Error code:  {error}')
        self.log.info(f'Error msg:  {error_msg}')
# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.nlp_controller import NlpController


CREDENTIALS_FILE = f'res:client_service_key.json'


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Speech to text with file example')
        self.nlp: NlpController = await self.enable_controller('nlp')
        await self.nlp.stt_set_provider(
                self.provider, 
                credentials_file=CREDENTIALS_FILE)


    async def loop(self):
        text = await self.nlp.stt_transcribe_from_file(
                file=self.file, 
                language=self.language, 
                wait=True
            )
        self.log.info(f'Result: {text}')
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.provider = self.get_argument(
                '-p', '--provider', 
                default='google_stt', # openai_stt
                help='provider to use'
            )
        self.file = self.get_argument(
                '-v', '--voice-detector', 
                type=str, 
                default='res:test.wav',
                help='file to use'
            )      
        self.language = self.get_argument(
                '-l', '--language', 
                type=str, 
                default='en-US', # 'en'
                help='voice language, may change depending the provider'
            )  

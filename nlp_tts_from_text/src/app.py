# System Imports

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.nlp_controller import NLPController


# If coqui
PROVIDER = 'coqui_tts'
VOICE = 'male-en-2'
# If google
# PROVIDER = 'google_tts'
# VOICE = 'us'

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('Ra-Ya Py - Text to Speeach Example')
        self.nlp: NLPController = await self.enable_controller('nlp')
        await self.nlp.tts_set_provider(
                self.provider
            )


    async def loop(self):
        await self.nlp.tts_play_text(
                text=self.text, 
                voice=self.voice,
                language=self.language,
                callback_feedback=self.cb_transcribe_feedback,
                wait=True,
            )
        self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.provider = self.get_argument(
                '-p', '--provider', 
                type=str, 
                required=False,
                default='google_tts',
                help='text to speech provider'
            )        
        self.text = self.get_argument(
                '-t', '--text', 
                type=str, 
                nargs='+',
                required=True,
                help='text to use in speech'
            )
        self.voice = self.get_argument(
                '-v', '--voice', 
                type=str, 
                required=False,
                default='us',
                help='voice to use in the speech'
            )        
        self.language = self.get_argument(
                '-l', '--language', 
                type=str, 
                required=False,
                default='en',
                help='Language to use in the speech'
            )  
        self.text = ' '.join(self.text)


    def cb_transcribe_feedback(self, feedback_code, feedback_msg):
        # self.log.info(f'State code:  {feedback_code}')
        self.log.info(f'State msg:  {feedback_msg}')
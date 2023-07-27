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
                credentials_file=CREDENTIALS_FILE)


    async def loop(self):
        print('AAA')
        text = await self.nlp.stt_transcribe_from_file('res:test.wav', 'en-US')
        self.log.info(f'Result: {text}')
        # self.finish_app()


    async def finish(self):
        self.log.info('Ra-Ya application finished')


# class RayaApplication(RayaApplicationBase):

#     async def setup(self):
#         self.log.info('Ra-Ya Py - Computer Vision Tag Detection Example')
#         self.nlp: NlpController = await self.enable_controller('nlp')
#         await self.nlp.stt_set_provider(
#                 'openai_stt')


#     async def loop(self):
#         print('AAA')
#         # Language 'en-US' for google and 'en' for openai 
#         text = await self.nlp.stt_transcribe_from_file('res:test.wav', 'en')
#         self.log.info(f'Result: {text}')
#         # self.finish_app()


#     async def finish(self):
#         self.log.info('Ra-Ya application finished')

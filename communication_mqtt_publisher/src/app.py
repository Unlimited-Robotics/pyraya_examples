import json

from raya.application_base import RayaApplicationBase
from raya.controllers.communication_controller import CommunicationController
from raya.exceptions import RayaCommNotRunningApp


LOOP_DELAY = 3.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('MQTT Publisher\n')
        self.comm:CommunicationController = \
                await self.enable_controller('communication')
        self.i = 0


    async def loop(self):
        data = {'text': 'Some text', 'counter': self.i}
        self.log.info(f'Publishing to topic \'{self.topic}\'')
        self.log.info(f'Data: \n{json.dumps(data, indent=2)}\n')
        try:
            await self.comm.mqtt_publish_message(self.topic, data)
        except RayaCommNotRunningApp:
            self.log.error('RGS not running')
            self.finish_app()
        await self.sleep(LOOP_DELAY)
        self.i += 1


    async def finish(self):
        self.log.info('APP FINISHED')


    def get_arguments(self):
        self.topic = self.get_argument(
                '--topic',
                help='topic',
                default='/namespace1/topic1',
            )

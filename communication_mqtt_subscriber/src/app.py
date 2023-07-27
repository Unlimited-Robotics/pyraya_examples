import json

from raya.application_base import RayaApplicationBase
from raya.controllers.communication_controller import CommunicationController
from raya.exceptions import RayaCommNotRunningApp


LOOP_DELAY = 3.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info('MQTT Subscriber\n')
        self.comm:CommunicationController = \
                await self.enable_controller('communication')
        await self.comm.mqtt_create_subscription(
                topic=self.topic,
                callback_async=self.cb_async_sub_topic,
            )
        self.log.info(f'Waiting messages from topic \'{self.topic}\'\n')


    async def loop(self):
        pass


    async def finish(self):
        self.log.info('APP FINISHED')


    async def cb_async_sub_topic(self, msg):
        self.log.info(f'Message received from topic \'{self.topic}\'')
        self.log.info(f'Data: \n{json.dumps(msg, indent=2)}\n')


    def get_arguments(self):
        self.topic = self.get_argument(
                '--topic',
                help='topic',
                default='/namespace1/topic1',
            )

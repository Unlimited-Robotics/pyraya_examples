from raya.application_base import RayaApplicationBase
from raya.controllers.communication_controller import CommunicationController
from raya.exceptions import RayaCommNotRunningApp


LOOP_DELAY = 1.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.comm:CommunicationController = \
                await self.enable_controller('communication')
        self.comm.create_incoming_msg_listener(
                callback=self.cb_incoming_msg
            )
        self.i = 0


    async def loop(self):
        msg = {'text': 'hello world', 'counter': self.i}
        self.log.info(f'Sending message to GGS server:')
        self.log.info(f'  {msg}')
        self.log.info(f'')
        try:
            await self.comm.send_msg(msg)
        except RayaCommNotRunningApp:
            self.log.warn('GGS not running yet')
            self.finish_app()
        await self.sleep(LOOP_DELAY)


    async def finish(self):
        pass


    def cb_incoming_msg(self, msg):
        self.log.info(f'Message received:')
        self.log.info(f'  msg: {msg}')
        self.log.info(f'')

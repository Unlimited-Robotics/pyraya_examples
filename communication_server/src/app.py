from raya.application_base import RayaApplicationBase
from raya.controllers.communication_controller import CommunicationController
from raya.exceptions import RayaCommNotRunningApp


GOAL_APP_ID = 'communication_client'
LOOP_DELAY = 3.0


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.comm:CommunicationController = \
                await self.enable_controller('communication')
        self.comm.create_incoming_msg_listener(
                callback=self.cb_incoming_msg
            )


    async def loop(self):
        msg = {'some_string': 'hello', 'some_number': self.i}
        self.log.info(f'Sending message to app \'{GOAL_APP_ID}\':')
        self.log.info(f'  {msg}')
        self.log.info(f'')
        try:
            await self.comm._server_send_msg_to_app(
                    message=msg, 
                    goal_app_id=GOAL_APP_ID
                )
        except RayaCommNotRunningApp:
            self.log.warn(f'App \'{GOAL_APP_ID}\' not running yet')
            self.finish_app()
        await self.sleep(3.0)
        self.i += 1


    async def finish(self):
        pass


    def cb_incoming_msg(self, msg, origin_app_id):
        self.log.info(f'Message received from application \'{origin_app_id}\'')
        self.log.info(f'  {msg}')
        self.log.info(f'')

from raya.application_base import RayaApplicationBase
from raya.enumerations import TELEOPERATION_STATUS


class RayaApplication(RayaApplicationBase):

    async def setup(self):

        self.teleop = await self.enable_controller('teleoperation')
        self.teleop.register_request_callback(self.cb_teleop_request)
        self.teleop.register_finish_callback(self.cb_teleop_finished)

        # At the begining the teeloperation is not available
        self._available_for_teleop = False

        # Showing messages in teeloperation software GUI
        self.log.info(f'Send popup to the teleoperator')
        await self.teleop.send_command(
                command="popup",
                msg='{"message": "Hello from app!", "time": "10", "color": "#FFFF00"}',
            )
        
        # After 10 seconds, the teleoperation gets available
        await self.sleep(10.0)
        self._available_for_teleop = True


    async def loop(self):
        # Check the status every 5 seconds
        await self.sleep(2.0)
        self.log.info(f'App id: "{str(self.teleop._app_id)}"')
        self.log.info(f'Teleoperation status: {str(self.teleop.get_status())}')


    async def finish(self):
        await self.teleop.finish_teleoperation()
        self.log.info(f'Hello from finish()')


    async def cb_teleop_request(self):
        self.log.info('Teleoperation requested...')
        if self._available_for_teleop:
            await self.teleop.start_teleoperation()
            self.log.warn('Accepted')
        else:
            await self.teleop.reject_teleoperation()
            self.log.warn('Rejected')


    async def cb_teleop_finished(self):
        print(f'Teleoperation finished')
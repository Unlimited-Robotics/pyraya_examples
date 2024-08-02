from raya.application_base import RayaApplicationBase
from raya.controllers.teleoperation_controller import NOT_CONNECTED, NOT_AVAILABLE, TELEOPERATING, REQUESTING, IDLE

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Hello from setup()')
        self.teleop = await self.enable_controller('teleoperation')
        self.teleop.register_request_callback(self.print_status)
        self.teleop.register_finish_callback(self.finish_teleop)

    async def loop(self):
        await self.teleop.send_msg(
            msg="Hello from app",
            time=10,
            color="#FFFF00"
            )
        await self.sleep(20.0)
        self.finish_app()

    async def finish(self):
        self.log.info(f'Hello from finish()')

    async def print_status(self, status: int):
        names = ["NOT_CONNECTED", "NOT_AVAILABLE", "TELEOPERATING", "REQUESTING", "IDLE"]
        print(f'Engine status: {names[status]}')
        if status == REQUESTING:
            await self.teleop.start_teleoperation()
            # await self.sleep(2.0)
    
    async def finish_teleop(self):
        print(f'Finish teleoperation')
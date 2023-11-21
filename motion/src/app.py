from raya.controllers.motion_controller import MotionController
from raya.application_base import RayaApplicationBase
from raya.enumerations import ANGLE_UNIT


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.motion_flag = False
        self.motion:MotionController = await self.enable_controller('motion')


    async def loop(self):

        self.log.info('Rotating 90 degrees left at 20 deg/sec')
        await self.motion.rotate(
                angle=90.0, 
                angular_speed=20.0, 
                ang_unit=ANGLE_UNIT.DEGREES, 
                wait=True
            )
        self.log.info('Motion command finished'); 
        self.log.info('')

        self.log.info(
                'Rotating 1.5708 radians left (90 degrees) at 0.349 rads/sec'
            )
        self.motion_flag = True
        await self.motion.rotate(
                angle=1.5708, 
                angular_speed=-0.349, 
                ang_unit=ANGLE_UNIT.RADIANS,
                callback_finish=self.cb_motion_finished
            )
        while self.motion_flag: 
            await self.sleep(0.1)
        self.log.info('Motion command finished'); 
        self.log.info('')

        self.log.info('Moving forward 0.5 meters at 0.2 m/s')
        await self.motion.move_linear(
                distance=0.5, 
                x_velocity=0.2, 
                wait=True
            )
        self.log.info('Motion command finished'); self.log.info('')

        self.log.info('Moving backward 0.5 meters at 0.3 m/s')
        await self.motion.move_linear(
                distance=0.5, 
                x_velocity=-0.3
            )
        while self.motion.is_moving(): 
            await self.sleep(0.1)
        self.log.info('Motion command finished'); 
        self.log.info('')

        self.log.info('Moving forward at 0.3 m/s for 2.0 seconds')
        await self.motion.set_velocity(
                x_velocity=0.3, 
                y_velocity=0.0, 
                angular_velocity=0.0, 
                duration=2.0
            )
        await self.motion.await_until_stop()
        self.log.info('Motion command finished'); 
        self.log.info('')

        self.log.info('Moving backward at 0.3 m/s and rotate at 10 deg/sec')
        await self.motion.set_velocity(
                x_velocity=0.3, 
                y_velocity=0.0, 
                angular_velocity=10.0, 
                duration=10.0,
                ang_unit=ANGLE_UNIT.DEGREES, 
                wait=False, 
                callback_finish=self.cb_motion_finished,
                callback_feedback=self.cb_motion_feedback
            )
        self.log.info('for 20 seconds')
        await self.sleep(2.0)
        self.log.info('Canceling motion after 2.0 seconds')
        await self.motion.cancel_motion()
        self.log.info('Motion command finished'); 
        self.log.info('')
        
        self.finish_app()


    async def finish(self):
        try:
            if self.motion.is_moving():
                self.log.info('Stopping motion')
                await self.motion.cancel_motion()
        except AttributeError:
            pass
        self.log.info('Finish app called')


    def cb_motion_feedback(self, 
                feedback_code, 
                feedback_msg, 
                time_left, 
                nearby_obstacle
            ):
        self.log.info(f'Motion feedback: {time_left}')


    def cb_motion_finished(self, 
                error_code, 
                error_msg, 
                interrupted, 
                obstacle_type
            ):
        self.log.info('Motion finished callback called!')
        if error_code != 0:
            self.log.info(f'Motion command error {error_code}: {error_msg}')
        self.motion_flag = False

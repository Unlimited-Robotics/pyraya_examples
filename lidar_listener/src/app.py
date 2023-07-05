from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.controllers.motion_controller import MotionController
from raya.enumerations import ANG_UNIT


SPINNING_VELOCITIES = {
        'x_velocity':0.0, 
        'y_velocity':0.0, 
        'angular_velocity':-20.0
    }


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling lidar controller')
        self.lidar:LidarController = await self.enable_controller('lidar')

        self.log.info(f'Enabling listener for lidar')
        self.lidar.create_obstacle_listener(
                listener_name='obstacle',
                callback=self.callback_obstacle,
                lower_angle=0,
                upper_angle=10,
                upper_distance=1.0, 
                ang_unit=ANG_UNIT.DEG,
            )

        # If spin parameter was set
        if self.spin_ena:
            self.log.info(f'Spin option enabled')
            self.log.info(f'Enabling motion controller')
            self.motion = await self.enable_controller('motion')
            self.log.info(f'Starting motion')
            await self.motion.set_velocity(
                    **SPINNING_VELOCITIES, 
                    duration=self.duration,
                )
        
        self.create_timer(name='duration', timeout=self.duration)


    async def loop(self):
        if self.is_timer_done('duration'):
            self.finish_app()


    async def finish(self):
        if self.spin_ena and self.motion.is_moving():
            self.log.info('Stopping robot movement...')
            await self.motion.cancel_motion()
        self.lidar.delete_listener(listener_name='obstacle')
        self.log.info('App finished')


    def get_arguments(self):
        self.spin_ena = self.get_flag_argument(
                '-s', '--spin',
                help='Spins while scanning'
            )
        self.duration = self.get_argument(
                '-d', '--duration',
                type=float,
                help='Scanning duration',
                default=10.0
            )


    def callback_obstacle(self):
        self.log.warning('Obstacle!')

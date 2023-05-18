import json
import matplotlib.pyplot as plt
import numpy as np


from raya.application_base import RayaApplicationBase
from raya.controllers.lidar_controller import LidarController
from raya.controllers.lidar_controller import ANG_UNIT


SPINNING_VELOCITIES = {
        'x_velocity':0.0, 
        'y_velocity':0.0, 
        'angular_velocity':-20.0
    }


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.obstacle_counter = 0

        self.log.info(f'Enabling lidar controller')
        self.lidar:LidarController = await self.enable_controller('lidar')

        self.log.info('Laser info:')
        self.lidar_info = self.lidar.get_laser_info(ang_unit = ANG_UNIT.RAD)
        self.log.info(json.dumps(self.lidar_info, indent=2))

        fig = plt.figure()
        self.ax1 = fig.add_subplot(111, projection='polar')
        
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
        self.update_lidar_plot()
        # Check obstacle
        if self.lidar.check_obstacle(
                    lower_angle=0, 
                    upper_angle=45,
                    upper_distance=2.0, 
                    ang_unit=ANG_UNIT.DEG
                ):
            self.obstacle_counter += 1
            self.log.info(f'Obstacle {self.obstacle_counter}')

        if self.is_timer_done('duration'):
            self.finish_app()

        await self.sleep(self.period)
        

    async def finish(self):
        if self.spin_ena and self.motion.is_moving():
            self.log.info('Stopping robot movement...')
            await self.motion.cancel_motion()
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
        self.period = self.get_argument(
                '-p', '--period',
                type=float,
                help='Scanning period',
                default=1.0
            )


    def update_lidar_plot(self):
        # Get data
        raw_data = self.lidar.get_raw_data()
        theta = np.linspace(
                self.lidar_info['angle_min'], 
                self.lidar_info['angle_max'], 
                len(raw_data)
            )
        # Plot
        self.ax1.clear()
        self.ax1.scatter(x=-np.array(theta)-1.578, y=raw_data, s=2)
        self.ax1.set_ylim(0.0, 10.0)
        plt.pause(0.001) # Needed for real time plotting

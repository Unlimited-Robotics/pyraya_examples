from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.motion_controller import MotionController
from raya.tools.image import show_image


SPINNING_VELOCITIES = {
        'x_velocity':0.0, 
        'y_velocity':0.0, 
        'angular_velocity':-20.0
    }


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling cameras controller')
        self.cameras: CamerasController = \
                                    await self.enable_controller('cameras')
        
        # Check if selected camera is available
        available_cameras = self.cameras.available_cameras()
        if not self.camera_name in available_cameras:
            self.log.error(f'Camera \'{self.camera_name}\' not available')
            self.log.info('Available cameras:')
            for camera in available_cameras:
                self.log.info(f'  - {camera}')
            self.abort_app()

        self.log.info(f'Enabling camera \'{self.camera_name}\'')
        await self.cameras.enable_camera(camera_name=self.camera_name)
        self.log.info(f'Enabling listener for camera \'{self.camera_name}\'')
        self.cameras.create_frame_listener(
                camera_name=self.camera_name,
                callback=self.callback_color_frame,
            )
        self.log.info(f'Camera \'{self.camera_name}\' enabled')

        # If spin parameter was set
        if self.spin_ena:
            self.log.info(f'Spin option enabled')
            self.log.info(f'Enabling motion controller')
            self.motion:MotionController = \
                    await self.enable_controller('motion')
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
        self.log.info('Disabling camera...')
        await self.cameras.disable_camera(self.camera_name)
        if self.spin_ena and self.motion.is_moving():
            self.log.info('Stopping robot movement...')
            await self.motion.cancel_motion()
        self.log.info('App finished')


    def get_arguments(self):
        self.camera_name = self.get_argument(
                '-c', '--camera-name',
                help='camera to visualize',
                required=True,
            )
        self.duration = self.get_argument(
                '-d', '--duration',
                type=float,
                help='visualizing duration in seconds',
                default=20.0,
            )
        self.spin_ena = self.get_flag_argument(
                '-s', '--spin',
                help='enable to make the robot spin during visualizing',
            )
        self.vis_scale = self.get_argument(
                '--scale',
                type=float,
                help='scale from the camera image to the visualization window',
                default=0.4,
            )


    def callback_color_frame(self, img):
        show_image(
                img=img, 
                title=f'Camera {self.camera_name}', 
                scale=self.vis_scale
            )

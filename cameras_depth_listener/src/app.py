from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.motion_controller import MotionController
from raya.tools.image import show_image
from raya.enumerations import IMAGE_TYPE
import cv2
import asyncio


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.log.info(f'Enabling cameras controller')
        self.cameras: CamerasController = \
                                    await self.enable_controller('cameras')
        
        # Check if selected depth camera is available
        available_cameras = self.cameras.available_cameras(IMAGE_TYPE.DEPTH)
        if not self.camera_name in available_cameras:
            self.log.error(f'Camera \'{self.camera_name}\' not available')
            self.log.info('Available depth cameras:')
            for camera in available_cameras:
                self.log.info(f'  - {camera}')
            self.abort_app()

        self.log.info(f'Enabling camera \'{self.camera_name}\'')
        await self.cameras.enable_camera(camera_name=self.camera_name, img_type=IMAGE_TYPE.DEPTH)
        self.log.info(f'Enabling listener for camera \'{self.camera_name}\'')
        self.cameras.create_frame_listener(
                camera_name=self.camera_name,
                callback=self.callback_color_frame,
                img_type=IMAGE_TYPE.DEPTH
            )
        self.log.info(f'Depth camera \'{self.camera_name}\' enabled')
        self.create_timer(name='duration', timeout=self.duration)


    async def loop(self):
        if self.is_timer_done('duration'):
            self.finish_app()


    async def finish(self):
        self.log.info('Disabling camera...')
        await self.cameras.disable_camera(self.camera_name, IMAGE_TYPE.DEPTH)
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
        self.vis_scale = self.get_argument(
                '--scale',
                type=float,
                help='scale from the camera image to the visualization window',
                default=0.4,
            )


    def callback_color_frame(self, img):
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                asyncio.create_task(self.handle_mouse_click(x, y))

        cv2.namedWindow(f'Camera {self.camera_name}')
        cv2.setMouseCallback(f'Camera {self.camera_name}', mouse_callback)
        show_image(
            img=img,
            title=f'Camera {self.camera_name}',
            scale=self.vis_scale,
            img_type=IMAGE_TYPE.DEPTH
        )


    async def handle_mouse_click(self, x, y):
        point_3D = await self.cameras.get_3D_point(self.camera_name, (y, x))
        print(f"3D Point at ({x}, {y}): {point_3D}")
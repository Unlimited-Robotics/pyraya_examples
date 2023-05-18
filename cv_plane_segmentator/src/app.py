# System Imports
import json
import collections
import numpy as np
import random
import open3d as o3d

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController


class RayaApplication(RayaApplicationBase):
    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision Object Segmentation Example')

        self.last_segmentations = None
        self.last_segmentations_timestamp = None
        self.last_color_frames = collections.deque(maxlen=60)

        # Cameras
        self.cameras: CamerasController = \
                await self.enable_controller('cameras')
        self.available_cameras = self.cameras.available_color_cameras()
        self.log.info('Available cameras:')
        self.log.info(f'  {self.available_cameras}')

        # If a camera name was set
        if self.camera != None:
            cams = set(self.available_cameras)
            if self.camera in cams:
                self.working_camera = self.camera
            else:
                self.log.info('Camera name not available')
                self.finish_app()
                return
        else:
            # If a camera name wasn't set it works with camera in zero position
            self.working_camera = self.available_cameras[0]

        # Enable camera
        await self.cameras.enable_color_camera(self.working_camera)

        # Computer Vision
        self.cv: CVController = await self.enable_controller('cv')
        self.available_models = await self.cv.get_available_models()
        self.log.info('Available Computer Vision models:')

        # Pretty print
        self.log.info(json.dumps(self.available_models, indent=2))

        # Enable segmentator
        self.log.info('Enabling model...')
        self.segmentator = await self.cv.enable_model(
                name=str(self.model),
                source=str(self.working_camera),
                continues_msg=False,
            )
        self.log.info('Model enabled')


    async def loop(self):
        self.last_segmentations, self.last_segmentations_timestamp = \
            await self.segmentator.get_segmentations_once(get_timestamp=True)
        self.get_planes()
        self.finish_app()
            
        
    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model_obj=self.segmentator)
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--ransac', 
                default='yolov5s_coco',
                help='segmentator model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )
        

    def callback_all_planes(self, segmentations, timestamp):
        self.last_segmentations = list(segmentations.values())
        self.last_segmentations_timestamp = timestamp
        

    def get_planes(self):
        planes = []
        colors = [] 
        for segmentation in self.last_segmentations:
            points = np.array(
                    segmentation['points'], 
                    dtype=np.float32
                ).reshape((-1, 3))
            r = random.random()
            g = random.random()
            b = random.random()
            color = np.zeros((points.shape[0], points.shape[1]))
            color[:, 0] = r
            color[:, 1] = g
            color[:, 2] = b
            planes.append(points)
            colors.append(color)  
        if len(planes) > 0: 
            planes = np.concatenate(planes, axis=0)
            colors = np.concatenate(colors, axis=0)
            self.draw_result(points=planes, colors=colors)


    def draw_result(self, points, colors):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        o3d.visualization.draw_geometries([pcd])

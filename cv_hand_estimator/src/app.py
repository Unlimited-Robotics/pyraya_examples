# System Imports
import json
import cv2
import collections
import numpy as np

# Raya Imports
from raya.application_base import RayaApplicationBase
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.cv_controller import CVController


class RayaApplication(RayaApplicationBase):
    
    async def setup(self):
        self.log.info('Ra-Ya Py - Computer Vision hand estimation Example')
        self.i = 0
        self.last_estimations = None
        self.last_estimations_timestamp = None
        self.last_color_frames = collections.deque(maxlen=10)

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

        # Enable estimator
        self.log.info('Enabling model...')
        self.estimator = await self.cv.enable_model(
                name=self.model,
                source=self.working_camera
            )
        self.log.info('Model enabled')

        # Create listener
        self.cameras.create_color_frame_listener(
                camera_name=self.working_camera,
                callback=self.callback_color_frame
            )
        self.estimator.set_estimations_callback(
                callback=self.callback_all_hands,
                as_dict=True,
                call_without_estimations=True,
            )


    async def loop(self):
        await self.sleep(1.0)
        if self.i > 50:
            self.finish_app()
        self.i += 1
        

    async def finish(self):
        self.log.info('Disabling model...')
        await self.cv.disable_model(model='estimator', type='hand_pose')
        self.log.info('Disabling camera...')
        await self.cameras.disable_color_camera(self.working_camera)
        self.log.info('Ra-Ya application finished')


    def get_arguments(self):
        self.model = self.get_argument(
                '-m', '--model', 
                default='mp_hand_pose',
                help='face model name'
            )
        self.camera = self.get_argument(
                '-c', '--camera-name', 
                type=str, 
                required=True,
                help='name of camera to use'
            )


    def callback_all_hands(self, estimations, timestamp):
        self.last_estimations = list(estimations.values())
        self.last_estimations_timestamp = timestamp
        self.match_image_estimations()


    def callback_color_frame(self, image, timestamp):
        self.last_color_frames.append( (timestamp, image) )
        self.match_image_estimations()


    def match_image_estimations(self):
        if self.last_estimations_timestamp is None or \
                not self.last_color_frames:
            return
        image = None
        for color_frame in self.last_color_frames:
            if color_frame[0] == self.last_estimations_timestamp:
                image = color_frame[1].copy()
        if image is None:
            return
        # Draw results on the input image
        frame, view_3d = self.visualize(
                image=image, 
                hands=self.last_estimations
            )
        cv2.imshow('MediaPipe Handpose Detection Demo', frame)
        cv2.imshow('3D HandPose Demo', view_3d)
        cv2.waitKey(1)    


    def visualize(self, image, hands):
        display_screen = image.copy()
        display_3d = np.zeros((400, 400, 3), np.uint8)
        cv2.line(
                img=display_3d, 
                pt1=(200, 0),
                pt2=(200, 400), 
                color=(255, 255, 255),
                thickness=2
            )
        cv2.line(
                img=display_3d, 
                pt1=(0, 200), 
                pt2=(400, 200), 
                color=(255, 255, 255), 
                thickness=2
            )
        cv2.putText(
                img = display_3d, 
                text = 'Main View', 
                org = (0, 12), 
                fontFace = cv2.FONT_HERSHEY_DUPLEX, 
                fontScale = 0.5, 
                color = (0, 0, 255)
            )
        cv2.putText(
                img = display_3d, 
                text = 'Top View', 
                org = (200, 12), 
                fontFace = cv2.FONT_HERSHEY_DUPLEX, 
                fontScale = 0.5, 
                color = (0, 0, 255)
            )
        cv2.putText(
                img = display_3d, 
                text = 'Left View', 
                org = (0, 212), 
                fontFace = cv2.FONT_HERSHEY_DUPLEX, 
                fontScale = 0.5, 
                color = (0, 0, 255)
            )
        cv2.putText(
                img = display_3d, 
                text = 'Right View', 
                org = (200, 212), 
                fontFace = cv2.FONT_HERSHEY_DUPLEX, 
                fontScale = 0.5, 
                color = (0, 0, 255)
            )
        is_draw = False  # ensure only one hand is drawn
        for handpose in hands:
            bbox = handpose['bbox']
            handedness_text = handpose['handedness']
            landmarks_screen = np.reshape(handpose['landmarks'], (21, 3))
            landmarks_word = np.reshape(handpose['world_landmarks'], (21, 3))
            # draw box
            cv2.rectangle(
                    img = display_screen, 
                    pt1 = (bbox[0], bbox[1]), 
                    pt2 = (bbox[2], bbox[3]), 
                    color = (0, 255, 0), 
                    thickness = 2
                )
            # draw handedness
            cv2.putText(
                    img = display_screen, 
                    text = '{}'.format(handedness_text), 
                    org = (bbox[0], bbox[1] + 12), 
                    fontFace = cv2.FONT_HERSHEY_DUPLEX, 
                    fontScale = 0.5, 
                    color = (0, 0, 255)
                )
            # Draw line between each key points
            landmarks_xy = landmarks_screen[:, 0:2]
            self.draw_lines(
                    image=display_screen,
                    landmarks=landmarks_xy, 
                    is_draw_point=False
                )
            # z value is relative to WRIST
            for p in landmarks_screen:
                r = max(5 - p[2] // 5, 0)
                r = min(r, 14)
                cv2.circle(
                        img = display_screen, 
                        center = np.array([p[0], p[1]]), 
                        radius = r, 
                        color = (0, 0, 255), 
                        thickness = -1
                    )

            if is_draw is False:
                is_draw = True
                # Main view
                landmarks_xy = landmarks_word[:, [0, 1]]
                landmarks_xy = (landmarks_xy * 1000 + 100).astype(np.int32)
                self.draw_lines(
                        image=display_3d, 
                        landmarks=landmarks_xy, 
                        thickness=5
                    )

                # Top view
                landmarks_xz = landmarks_word[:, [0, 2]]
                landmarks_xz[:, 1] = -landmarks_xz[:, 1]
                landmarks_xz = (landmarks_xz * 1000 + \
                                np.array([300, 100])).astype(np.int32)
                self.draw_lines(
                        image=display_3d, 
                        landmarks=landmarks_xz, 
                        thickness=5
                    )

                # Left view
                landmarks_yz = landmarks_word[:, [2, 1]]
                landmarks_yz[:, 0] = -landmarks_yz[:, 0]
                landmarks_yz = (landmarks_yz * 1000 + \
                                np.array([100, 300])).astype(np.int32)
                self.draw_lines(
                        image=display_3d, 
                        landmarks=landmarks_yz, 
                        thickness=5)

                # Right view
                landmarks_zy = landmarks_word[:, [2, 1]]
                landmarks_zy = (landmarks_zy * 1000 + \
                                np.array([300, 300])).astype(np.int32)
                self.draw_lines(
                        image=display_3d, 
                        landmarks=landmarks_zy, 
                        thickness=5
                    )

        return display_screen, display_3d


    def draw_lines(self, image, landmarks, is_draw_point=True, thickness=2):
        connections = [[i, i+1] for i in range(0, 21, 5) for j in range(4)]
        for connection in connections:
            cv2.line(
                    img=image, 
                    pt1=landmarks[connection[0]], 
                    pt2=landmarks[connection[1]], 
                    color=(255, 255, 255), 
                    thickness=thickness
                )
            if is_draw_point:
                for p in landmarks:
                    cv2.circle(
                            img=image, 
                            center=p, 
                            radius=thickness, 
                            color=(0, 0, 255), 
                            thickness=-1
                        )
                    
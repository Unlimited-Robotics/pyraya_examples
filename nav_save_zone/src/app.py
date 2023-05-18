import cv2
import math
import pygame
import numpy as np
from math import ceil
from pygame.locals import *

from raya.application_base import RayaApplicationBase
from raya.controllers.navigation_controller import POS_UNIT, ANG_UNIT
from raya.exceptions import RayaNavNotNavigating, RayaNavInvalidGoal
from raya.controllers.navigation_controller import NavigationController


GARY_DIMENSION = [0.6, 0.4]


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        pygame.init()
        self.navigation: NavigationController = \
                await self.enable_controller('navigation')
        self.screen = pygame.display.set_mode(
                size=(500, 500), 
                flags=RESIZABLE
            )
        self.list_of_maps = await self.navigation.get_list_of_maps()
        self.log.info(f'List of maps: {self.list_of_maps}')
        self.log.info((
                f'Setting map: {self.map_name}. '
                'Waiting for the robot to get localized'
            ))
        robot_localized = await self.navigation.set_map(
                map_name=self.map_name, 
                wait_localization=True, 
                timeout=3.0,
                callback_feedback=None,
                callback_finish=None
            )
        if not robot_localized:
            self.log.error(f'Robot couldn\'t localize itself')
            self.finish_app()
        self.log.info(f'Localized. Using map \'{self.map_name}\'')
        self.map_image, self.map_info = \
                await self.navigation.get_map(map_name=self.map_name)
        await self.update_and_draw_zones()
        self.gary_img = pygame.image.load('./dat/gary.png')
        self.gary_img_dimension = [
                self.gary_img.get_width(), 
                self.gary_img.get_height()
            ]
        self.gary_footprint = tuple([
                ceil(GARY_DIMENSION[0]/self.map_info['resolution']), 
                ceil(GARY_DIMENSION[1]/self.map_info['resolution']),
            ])
        self.pygame_img = self.cvimage_to_pygame(image=self.map_image)

        self.width_map = self.pygame_img.get_height()
        self.height_map = self.pygame_img.get_width()
        
        self.new_zone_points = np.empty(shape=(0,2), dtype=int)
        self.drawing = False
        self.new_zone_name = ''
        self.new_flag = False
        self.point_down = (0,0)
        self.new_goal = (0,0,0)


    async def loop(self):
        cv_map = self.map_image.copy()
        cv_map = cv2.polylines(
                img=cv_map, 
                pts=[self.new_zone_points], 
                isClosed=True, 
                color=(255, 0, 0), 
                thickness=5,
            )
        map_zones = self.cvimage_to_pygame(image=cv_map)
        w, h = pygame.display.get_surface().get_size()
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            await self.check_event(event=event, w=w, h=h)
        robot_position = await self.navigation.get_position(
                pos_unit=POS_UNIT.PIXEL,
                ang_unit=ANG_UNIT.RAD
            )
        x_pixel, y_pixel  = (robot_position[0], robot_position[1])
        degree_angle = math.degrees(robot_position[2]) - 90
        self.gary_scaled_footprint = self.pixels2pygame(
                x_pixel=self.gary_footprint[0], 
                y_pixel=self.gary_footprint[1], 
                w_screen=w, 
                h_screen=h
            )
        rotated_image = pygame.transform.rotate(
                self.gary_img.copy(), 
                degree_angle
            )
        self.gary_rotated_dimension = [
                rotated_image.get_width(), 
                rotated_image.get_height()
            ]
        gary_rotated_x = int(
                rotated_image.get_width() * self.gary_scaled_footprint[0]/ 
                self.gary_img_dimension[0]
            )
        gary_rotated_y = int(
                rotated_image.get_height() * self.gary_scaled_footprint[1]/ 
                self.gary_img_dimension[1]
            )
        gary_rotated_footprint = tuple([gary_rotated_x, gary_rotated_y])
        x_position = x_pixel - (gary_rotated_x/2)
        y_position = y_pixel - (gary_rotated_y)
        self.pos_new = tuple([
                int(x_position*w /self.height_map), 
                int(y_position*h/self.width_map)
            ])
        self.screen.blit(
                source=pygame.transform.scale(
                    surface=map_zones, 
                    size=(w, h)
                ), 
                dest=(0, 0)
            )
        self.screen.blit(
                source=pygame.transform.scale(
                    surface=rotated_image, 
                    size=gary_rotated_footprint
                ), 
                dest=self.pos_new
            )
        if self.new_flag:
            await self.send_nav_goal(
                    goal_x=self.new_goal[0], 
                    goal_y=self.new_goal[1], 
                    goal_angle=self.new_goal[2]
                )
        if self.drawing:
            self.show_buttons_save_cancel(w, h)
        else:
            self.show_button_draw(w, h)
            base_font = pygame.font.Font(None, 22)
            input_rect = pygame.Rect(w - 180, h - 30, 90, 30)
            pygame.draw.rect(self.screen, (255, 0, 0), input_rect)
            text_surface = base_font.render(
                    self.new_zone_name, 
                    True, 
                    (255, 255, 255)
                )
            self.screen.blit(
                    source=text_surface, 
                    dest=(input_rect.x+5, input_rect.y+5)
                )
        pygame.display.update()


    async def finish(self):
        pygame.quit()
        try:
            await self.navigation.cancel_navigation()
        except RayaNavNotNavigating:
            pass
        self.log.info('Finish app called')

    
    def get_arguments(self):
        self.map_name = self.get_argument(
                '-m', '--map-name',
                type=str,
                help='name of the new map',
                required=True,
            )

    
    def pixels2pygame(self, x_pixel, y_pixel, w_screen, h_screen):
        return tuple([
                ceil(x_pixel * w_screen / self.width_map), 
                ceil(y_pixel * h_screen / self.height_map),
            ])


    def pygame2pixel(self, x_pygame, y_pygame, w_screen, h_screen):
        return tuple([
                ceil(x_pygame  * self.height_map / w_screen), 
                ceil(y_pygame * self.width_map / h_screen),
            ])

    
    def show_button_draw(self, w, h):
        color_dark = (75, 231, 242)
        color_light = (50,50,50)
        pygame.draw.rect(
                surface=self.screen, 
                color=color_dark, 
                rect=[w - 80, h - 30, 80 , 30],
            )
        smallfont = pygame.font.SysFont(name='Corbel', size=16) 
        text = smallfont.render(
                'DRAW ZONE', 
                True, 
                color_light,
            )
        self.screen.blit(source=text , dest=(w - 75 , h - 20))
        label01 = smallfont.render(
                'Zone name = ', 
                True, 
                color_light,
            )
        self.screen.blit(source=label01 , dest=(w - 255 , h - 20))


    def show_buttons_save_cancel(self, w, h):
        color_dark = (6, 138, 1)
        color_light = (10, 10, 10)
        color_cancel  = (130, 7, 23)
        pygame.draw.rect(
                surface=self.screen, 
                color=color_dark, 
                rect=[w - 60, h - 30, 60 , 30]
            )
        smallfont = pygame.font.SysFont(
                name='Corbel',
                size=16,
            ) 
        text = smallfont.render(
                'SAVE', 
                True, 
                color_light,
            )
        self.screen.blit(
                source=text, 
                dest=(w - 45 , h - 20),
            )
        pygame.draw.rect(
                surface=self.screen, 
                color=color_cancel, 
                rect=[w - 125, h - 30, 60 , 30],
            )
        smallfont = pygame.font.SysFont(
                name='Corbel', 
                size=16,
            ) 
        text = smallfont.render(
                'CANCEL', 
                True, 
                color_light,
            )
        self.screen.blit(source=text , dest=(w - 117 , h - 20))


    async def update_and_draw_zones(self):
        self.zones = await self.navigation.get_zones(
                map_name=self.map_name
            )
        for zone in self.zones:
            color = tuple(np.random.choice(range(256), size=3))
            random_color = (int(color[0]), int(color[1]), int(color[2]))
            self.map_image = cv2.polylines(
                    img=self.map_image, 
                    pts=np.array([self.zones[zone]['zone_limits']]),
                    isClosed=True, 
                    color=random_color, 
                    thickness=4,
                )

    
    async def check_event(self, event, w, h):
        if event.type == QUIT:
            self.finish_app()
            return
        if event.type == pygame.KEYDOWN and not self.drawing:
            if event.key == pygame.K_BACKSPACE:
                self.new_zone_name = self.new_zone_name[:-1]
            elif event.key == pygame.K_KP_ENTER:
                self.drawing = True
            else:
                self.new_zone_name += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pos_click = pygame.mouse.get_pos()
            if not self.drawing:
                mouse_on_h_map_zone = w - 80 <= self.pos_click[0] <= w
                mouse_on_v_map_zone = h - 30 <= self.pos_click[1] <= h
                if mouse_on_h_map_zone and mouse_on_v_map_zone:
                    if self.new_zone_name != '':
                        self.drawing = True
                    else:
                        self.log.error((f'Zone_name empty'))
                else:
                    self.point_down = self.pygame2pixel(
                            x_pygame=self.pos_click[0], 
                            y_pygame=self.pos_click[1], 
                            w_screen=w, 
                            h_screen=h,
                        )
            else:
                mouse_on_h_tools_zone = w - 60 <= self.pos_click[0] <= w
                mouse_on_v_tools_zone = h - 30 <= self.pos_click[1] <= h
                mouse_on_h_cancel_zone = w - 125 <= self.pos_click[0] <= w - 65
                mouse_on_v_cancel_zone = h - 30 <= self.pos_click[1] <= h
                if mouse_on_h_tools_zone and mouse_on_v_tools_zone:
                    await self.navigation.save_zone(
                            map_name=self.map_name, 
                            zone_name=self.new_zone_name, 
                            points=self.new_zone_points.tolist(),
                            pos_unit = POS_UNIT.PIXEL,
                            wait=True
                        )
                    self.new_zone_points = np.empty((0,2),int)
                    self.new_zone_name = ''
                    self.drawing = False
                    await self.update_and_draw_zones()
                elif mouse_on_h_cancel_zone and mouse_on_v_cancel_zone:
                    self.new_zone_points = np.empty((0,2),int)
                    self.new_zone_name = ''
                    self.drawing = False
                else:
                    self.point_down = self.pygame2pixel(
                            x_pygame=self.pos_click[0], 
                            y_pygame=self.pos_click[1], 
                            w_screen=w, 
                            h_screen=h,
                        )
                    self.new_zone_points = np.concatenate((
                            self.new_zone_points, 
                            [[self.point_down[0], self.point_down[1]]]), 
                            axis=0
                        )
        if event.type == pygame.MOUSEBUTTONUP and not self.drawing:
            self.pos_click = pygame.mouse.get_pos()
            self.point_up = self.pygame2pixel(
                    x_pygame=self.pos_click[0], 
                    y_pygame=self.pos_click[1], 
                    w_screen=w, 
                    h_screen=h
                )            
            self.new_goal = (
                    self.point_down[0],
                    self.point_down[1],
                    -self.angle_between_points(
                            p1=self.point_down, 
                            p2=self.point_up,
                        )
                )
            self.new_flag = True


    async def send_nav_goal(self, goal_x, goal_y, goal_angle):
        if self.navigation.is_navigating():
            self.log.warn('Cancel current goal before send a new one.')
            self.new_flag = False
        else:
            self.log.warn(f'New goal received {self.new_goal}')
            try:
                await self.navigation.navigate_to_position( 
                    x=float(goal_x), 
                    y=float(goal_y), 
                    angle=goal_angle, 
                    pos_unit = POS_UNIT.PIXEL, 
                    ang_unit = ANG_UNIT.RAD,
                    callback_feedback = None,
                    callback_finish = None,
                    wait=False,
                )
            except RayaNavInvalidGoal:
                self.log.warn(f'Invalid goal')
            self.new_flag = False


    def cvimage_to_pygame(self, image):
        return pygame.image.frombuffer(
                image.tostring(), 
                image.shape[1::-1],
                'RGB',
            )


    def angle_between_points(self, p1, p2):
        return math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    
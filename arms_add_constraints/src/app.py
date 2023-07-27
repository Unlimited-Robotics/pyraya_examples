from raya.application_base import RayaApplicationBase
from raya.controllers.arms_controller import ArmsController
from raya.exceptions import *
from raya.enumerations import SHAPE_TYPE


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.arms: ArmsController = await self.enable_controller('arms')
        self.constraints_1 = {
            'joint_constraints': [
                {
                    'position': 0,
                    'joint_name': 'arm_right_shoulder_FR_joint',
                    'tolerance_above': 15,
                    'tolerance_below': 15,
                    'weight': 1.0,
                },
                {
                    'position': 0,
                    'joint_name': 'arm_right_shoulder_rail_joint',
                    'tolerance_above': 0.1,
                    'tolerance_below': 0,
                    'weight': 1.0,
                }
            ],
            'orientation_constraints': [
                {
                    'orientation': {'roll': 90},
                    'weight': 1.0,
                    'absolute_x_axis_tolerance': 20.0,
                    'absolute_y_axis_tolerance': 20.0,
                    'absolute_z_axis_tolerance': 180.0
                }
            ],
            'position_constraints': [
                {
                    'constraint_region': {
                        'types': [SHAPE_TYPE.BOX],
                        'shapes_poses': [{'position': {'x': 0,
                                                       'y': -1.02,
                                                       'z': 0.5},
                                          'orientation': {'pitch': 90}}],
                        'dimensions': [[2.0,
                                        1.0,
                                        0.95]]
                    },
                    'target_point_offset': {'x': 0.1, 'y': 0, 'z': 0},
                    'weight': 1.0,
                }
            ],
        }

        self.constraints_2 = {
            'joint_constraints': [
                {
                    'position': 0,
                    'joint_name': 'arm_right_shoulder_FR_joint',
                    'tolerance_above': 15,
                    'tolerance_below': 15,
                    'weight': 1.0,
                },
                {
                    'position': 0,
                    'joint_name': 'arm_right_shoulder_rail_joint',
                    'tolerance_above': 0.1,
                    'tolerance_below': 0,
                    'weight': 1.0,
                }
            ],
        }

        self.pose = {'x' : 0.36,
                'y' : -0.35,
                'z' : 0.58,
                'roll' : 0.0,
                'pitch' : 0.0,
                'yaw' : 0.0}
        
        
    async def loop(self):
        await self.arms.add_constraints(arm='right_arm', **self.constraints_1)
        try:
            await self.arms.set_pose(
                arm='right_arm',
                **self.pose,
                tilt_constraint= True,
                wait= True
            )
        except RayaArmsExternalException:
            self.log.warning(
                ('with this constraints is not possible plan to the'
                f' desired pose {self.pose}')) 
        await self.arms.remove_constraints(arm='right_arm')

        await self.arms.add_constraints(arm='right_arm', **self.constraints_2)
        await self.arms.set_pose(
            arm='right_arm',
            **self.pose,
            tilt_constraint= True,
            wait= True
        )
        await self.arms.remove_constraints(arm='right_arm')

        joints = await self.arms.get_current_joint_values(arm='right_arm')
        self.log.info(f'final joints values are: ')
        self.log.info('\t joint \t\t\t\t value')
        for joint, values in zip(joints['names'], joints['values']):
            self.log.info(f'{joint}  \t {values:.2f}')
        self.finish_app()


    async def finish(self):
        self.log.debug('Application finished successfully')

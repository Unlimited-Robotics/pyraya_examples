# JOINTS INCREMENTS
JOINT_INCREMENTS_ROTATIONAL = {
        1: 2.0,
        2: 10.0,
        3: -2.0,
        4: -10.0,
    }

JOINT_INCREMENTS_LINEAR = {
        1: 0.01,
        2: 0.05,
        3: -0.01,
        4: -0.05,
    }

# CLOSE/OPEN GRIPPER
GRIPPER_STATES = {
    0: {
        'desired_position': 0.0,
        'desired_pressure': 0.8,
    },
    1: {
        'desired_position': 1.0,
        'desired_pressure': 0.8,
    },
}

# POSE INCREMENTS
POSE_INCREMENTS = {
    1:  {'position': [+0.05, +0.00, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    2:  {'position': [+0.00, +0.05, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    3:  {'position': [+0.00, +0.00, +0.05], 'orientation': [+00.0, +00.0, +00.0]},
    4:  {'position': [+0.00, +0.00, +0.00], 'orientation': [+10.0, +00.0, +00.0]},
    
    5:  {'position': [-0.05, +0.00, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    6:  {'position': [+0.00, -0.05, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    7:  {'position': [+0.00, +0.00, -0.05], 'orientation': [+00.0, +00.0, +00.0]},
    8:  {'position': [+0.00, +0.00, +0.00], 'orientation': [-10.0, +00.0, +00.0]},

    9:  {'position': [+0.01, +0.00, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    10: {'position': [+0.00, +0.01, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    11: {'position': [+0.00, +0.00, +0.01], 'orientation': [+00.0, +00.0, +00.0]},
    12: {'position': [+0.00, +0.00, +0.00], 'orientation': [+02.0, +00.0, +00.0]},

    13: {'position': [-0.01, +0.00, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    14: {'position': [+0.00, -0.01, +0.00], 'orientation': [+00.0, +00.0, +00.0]},
    15: {'position': [+0.00, +0.00, -0.01], 'orientation': [+00.0, +00.0, +00.0]},
    16: {'position': [+0.00, +0.00, +0.00], 'orientation': [-02.0, +00.0, +00.0]},
}

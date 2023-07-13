from raya.enumerations import ANGLE_UNIT

ARMS_WAVE_TIMES = 2
ARMS_WAVE_ARM = 'right_arm'
ARMS_WAVE_POINTS = [
        [
            0.0,
            0.475,
            -0.1225,
            0.665,
            2.0944,
            -1.57,
            -0.08749999999999999,
            1.05,
        ],
        [
            0.0,
            0.475,
            -0.1225,
            0.665,
            2.0944,
            -1.57,
            -0.08749999999999999,
            0.05,
        ],
    ]
ARMS_WAVE_SEQUENCE = {
        'arm':ARMS_WAVE_ARM,
        'joint_values':ARMS_WAVE_TIMES*ARMS_WAVE_POINTS,
        'units':ANGLE_UNIT.RADIANS,
    }

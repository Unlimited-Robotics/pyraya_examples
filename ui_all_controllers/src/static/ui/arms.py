from raya.enumerations import INPUT_TYPE

from src.static.fs import *
from src.static.ui.general import DEFAULT_MAX_ITEMS_PER_PAGE

# SOUND

UI_ARMS_MAIN_SELECTOR = {
        'title': '🦾🦾 You would like to:', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
        'data': [
                {'id': 1, 'name': '⚙️ Show current joints values ⚙️'},
                {'id': 2, 'name': '🎯 Show current pose 🎯'},
                {'id': 3, 'name': '🏹 Move to predefined pose 🏹'},
                {'id': 4, 'name': '👋 Move joint 👋'},
                {'id': 5, 'name': '✊ Open/Close Gripper 🖐'},
                {'id': 6, 'name': '➡️ Cartesian Movement ➡️'},
                {'id': 7, 'name': '🔀 Execute Trajectory 🔀'},
                {'id': 8, 'name': '💾 Save Current Pose 💾'},
                {'id': 9, 'name': '🗑 Delete Pose 🗑'},
            ]
    }

UI_ARMS_SELECT_ARM = {
        'title': '🦾 Select an Arm 🦾',
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
    }

UI_ARMS_SELECT_JOINT = {
        'title': '⚙️ Select a Joint of Arm "{arm}" ⚙️', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
    }

UI_ARMS_SELECT_PREDEFINED_POSE = {
        'title': '🎯 Select a Predefined Pose of Arm "{arm}" 🎯', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
    }

UI_ARMS_JOINTS_CONTROLLER = {
        'title': '⚙️ Control the joint "{joint}" of arm "{arm}" ⚙️{limit_warn}', 
        'show_back_button': True,
        'data': [
                {'id': 1, 'name': '+'},
                {'id': 2, 'name': '+ +'},
                {'id': 3, 'name': '-'},
                {'id': 4, 'name': '- -'},
            ],
        'custom_style': {
                'selector': {
                        'font-size': '1000%',
                    }
            }
    }

UI_ARMS_LIMIT_WARNING = ' ⚠️ LIMIT REACHED ⚠️'

UI_ARMS_OPEN_CLOSE_GRIPPE = {
        'title': '✊ Open/Close Gripper of Arm "{arm}" 🖐', 
        'show_back_button': True,
        'data': [
                {'id': 0, 'name': '🖐 Open 🖐'},
                {'id': 1, 'name': '✊ Close ✊'},
            ],
    }  

UI_ARMS_CARTESIAN_CONTROLLER = {
        'title': '➡️ Control the arm "{arm}" ➡️{limit_warn}', 
        'show_back_button': True,
        'max_items_shown': 8,
        'data': [
                {'id': 1, 'name': 'X++'},
                {'id': 2, 'name': 'Y++'},
                {'id': 3, 'name': 'Z++'},
                {'id': 4, 'name': 'roll++'},

                {'id': 5, 'name': 'X--'},
                {'id': 6, 'name': 'Y--'},
                {'id': 7, 'name': 'Z--'},
                {'id': 8, 'name': 'roll--'},

                {'id': 9, 'name': 'X+'},
                {'id': 10, 'name': 'Y+'},
                {'id': 11, 'name': 'Z+'},
                {'id': 12, 'name': 'roll+'},

                {'id': 13, 'name': 'X-'},
                {'id': 14, 'name': 'Y-'},
                {'id': 15, 'name': 'Z-'},
                {'id': 16, 'name': 'roll-'},
            ],
    }

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
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

UI_ARMS_SELECT_ARM = {
        'title': '⚙️ Select a Joint ⚙️', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

UI_ARMS_SELECT_ARM = {
        'title': '🎯 Select a Predefined Pose 🎯', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

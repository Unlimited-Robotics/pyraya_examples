from src.static.fs import *
from raya.enumerations import INPUT_TYPE

#GENERAL

DEFAULT_MAX_ITEMS_PER_PAGE = 4

UI_CONTROLLER_SELECTOR = {
        'title': 'Which controller would you like to test?', 
        'show_back_button': False, 
        'data': [
                {'id': 1, 'name': '🔊 Sound 🔊'}, 
                {'id': 2, 'name': '🦾 Arms 🦾'}, 
                {'id': 3, 'name': '💃 Motion 💃'},
                {'id': 0, 'name': '❌ Finish App ❌'},
            ]
    }

UI_SCREEN_END = {
        'title':'Thanks!', 
        'subtitle':'Don\'t forget to subscribe and like 😉',
        'show_loader':False,
        'show_back_button': False, 
    }

UI_SCREEN_ERROR = {
        'title':'Error 💢', 
        'button_text':'OK',
        'custom_style':{
            'subtitle': {
                'text-align':'left',
                'font-family':'monospace',
            }
        }
    }

# SOUND

UI_SOUND_MAIN_SELECTOR = {
        'title': 'You would like to:', 
        'show_back_button': True, 
        'data': [
                {'id': 1, 'name': '🔊 Play a predefined sound 🔊'}, 
                {'id': 2, 'name': '🎶 Play a custom sound 🎶'}, 
                {'id': 3, 'name': '🎙 Record a sound 🎙'},
                {'id': 4, 'name': '📢 Play a pre-recorded sound 📢'},
            ]
    }

UI_SOUND_PLAY_PREDEFINED = {
        'title': '🔊 Play a predefined sound 🔊', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

UI_SOUND_PLAY_CUSTOM_SOUND = {
        'title': '🎶 Play a custom sound 🎶', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

UI_SOUND_NOT_CUSTOM_SOUNDS = {
        'title':'No Custom Sounds Available 🔇', 
        'subtitle':f'You can add .wav files to the folder {FS_SOUND_CUSTOM_FOLDER}',
        'show_back_button': True, 
    }

UI_SOUND_RECORD_TIME_SELECTOR = {
        'title': 'How much time would you like to record? 🎙⏲️', 
        'show_back_button': True, 
        'data': [
                {'id': 5,  'name': '5 seconds'}, 
                {'id': 10, 'name': '10 seconds'}, 
                {'id': 15, 'name': '15 seconds'},
                {'id': 0,  'name': 'Custom time'},
            ]
    }

UI_SOUND_RECORD_TIME_INPUT = {
        'title':'Time to record 🎙⏲️',
        'show_back_button': True,
        'input_type': INPUT_TYPE.NUMERIC,
    }

from raya.enumerations import INPUT_TYPE

from src.static.fs import *
from src.static.ui.general import DEFAULT_MAX_ITEMS_PER_PAGE

# SOUND

UI_SOUND_MAIN_SELECTOR = {
        'title': '🔊🔊 You would like to:',
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
        'data': [
                {'id': 1, 'name': '🔊 Play a predefined sound 🔊'}, 
                {'id': 2, 'name': '🎶 Play a custom sound 🎶'}, 
                {'id': 3, 'name': '🎙 Record a sound 🎙'},
                {'id': 4, 'name': '📢 Play a pre-recorded sound 📢'},
                {'id': 5, 'name': '🗑 Delete a pre-recorded sound 🗑'},
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
        'subtitle':
            f'You can add .wav files to the folder {FS_SOUND_CUSTOM_FOLDER}',
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
        'input_type': INPUT_TYPE.NUMERIC,
    }

UI_SOUND_RECORD_NAME_INPUT = {
        'title':'Name of the recording file to save 💾',
        'subtitle': 'The extension .wav will be added if not provided.',
        'input_type': INPUT_TYPE.TEXT,
    }

UI_SOUND_RECORDING = {
        'title':'🎙 Recording... '
    }

# TODO: When the UI title bug if fixed, remove the subtitle field
UI_ASK_PLAY_RECORDING = {
        'title':'Play Recorded Sound?',
        'subtitle':'Play Recorded Sound?',
        'submit_text':'YES',
        'cancel_text':'NO',
    }

UI_SOUND_PLAYING_RECORDING = {
        'title':'📢 Playing... ',
    }

UI_SOUND_PLAY_RECORDING = {
        'title': '📢 Play a recorded sound 📢', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

UI_SOUND_NOT_RECORDINGS = {
        'title':'No Recordings Available 🔇', 
        'subtitle':f'Use the \'Record a sound\' option to create recordings.',
        'show_back_button': True, 
    }

UI_SOUND_DELETE_RECORDING = {
        'title': '🗑 Delete a pre-recorded sound 🗑', 
        'show_back_button': True, 
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE
    }

# TODO: When the UI title bug if fixed, remove the subtitle field
UI_ASK_DELETE_RECORDING = {
        'title':'Delete Recording?',
        'subtitle':'Delete Recording?',
        'submit_text':'YES',
        'cancel_text':'NO',
    }
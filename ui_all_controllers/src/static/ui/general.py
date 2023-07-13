from src.static.fs import *
from raya.enumerations import UI_MODAL_TYPE

DEFAULT_MAX_ITEMS_PER_PAGE = 4

#GENERAL

UI_CONTROLLER_SELECTOR = {
        'title': 'Which controller would you like to test?', 
        'back_button_text': 'EXIT',
        'max_items_shown': DEFAULT_MAX_ITEMS_PER_PAGE,
        'data': [
                {'id': 1, 'name': '🔊 Sound 🔊'}, 
                {'id': 2, 'name': '🦾 Arms 🦾'}, 
                {'id': 3, 'name': '💃 Motion 💃'},
            ]
    }

UI_END = {
        'title':'Thanks!', 
        'subtitle':'Don\'t forget to subscribe and like 😉',
        'show_loader':False,
        'show_back_button': False, 
    }

UI_RAYA_EXCEPTION = {
        'title':'Ra-Ya Exception', 
        'submit_text':'OK',
        'cancel_text':'',
        'modal_type':UI_MODAL_TYPE.ERROR,
        'custom_style':{
            'subtitle': {
                'font-family':'monospace',
            },
            'content': {
                'text-align':'left',
                'font-family':'monospace',
            },
        },
    }

# TODO: When the UI title bug if fixed, remove the subtitle field
UI_ERROR_MUST_BE_NUMBER = {
        'title':'Value Error',
        'subtitle':'Value Error',
        'content':'Entered value must be numeric', 
        'submit_text':'OK',
        'cancel_text':'',
        'modal_type':UI_MODAL_TYPE.ERROR,
    }

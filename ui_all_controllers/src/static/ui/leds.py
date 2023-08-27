from raya.enumerations import UI_INPUT_TYPE

from src.static.fs import *
from src.static.ui.general import DEFAULT_MAX_ITEMS_PER_PAGE

# SOUND

UI_LEDS_MAIN_SELECTOR = {
        'title': 'Choose the animation that you want me to play :)', 
        'show_back_button': True, 
        'data': [
                {'id': 1, 'name': 'Waiting 🕧'},
                {'id': 2, 'name': 'Excited 🎊'},
                {'id': 3, 'name': 'Done 🟢'},
            ]
    }
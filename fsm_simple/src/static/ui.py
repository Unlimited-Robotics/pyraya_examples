from raya.enumerations import ANIMATION_TYPE

# SCREENS

UI_SCREEN_LOCALIZING = {
        'title':'Starting Application', 
        'subtitle':'Localizing 🕵',
    }

UI_SCREEN_FIRST_NAV_TO_HOME = {
        'title':'Starting Application', 
        'subtitle':'Going to home 🏠',
    }

UI_SCREEN_HOT = {
        'title':'It\'s too hot! 🥵', 
        'subtitle':'I can\'t work this way. Turn on the AC.',
    }

UI_SCREEN_FRESH = {
        'title':'Too much better!', 
        'subtitle':'It\'s fresh again 🥶',
    }

UI_SCREEN_NAV_TO_KITCHEN = {
        'title':'Yes Sr 🫡', 
        'subtitle':'Going to look for something to eat 🍌🌽🍔',
    }

UI_SCREEN_TAKE_PHOTO = {
        'title':'Nothing to eat 🍽', 
        'subtitle':'Consider going to the supermarket 🛒',
        'format':ANIMATION_TYPE.JPEG,
    }

UI_SCREEN_COME_BACK_WITHOUT_FOOD = {
        'title':'Coming back', 
        'subtitle':'But... without food 😔',
    }

UI_SCREEN_NAV_TO_BEDROOM = {
        'title':'Yes Sr 🫡', 
        'subtitle':'So tired, time to sleep 😴',
    }

UI_SCREEN_WAVING = {
        'title':'Hello 👋', 
        'subtitle':'The bed is really well done 🛏, I\'ll sleep later.',
    }

UI_SCREEN_COME_BACK_FROM_BEDROOM = {
        'title':'Coming back', 
        'subtitle':'After a really good nap. 🪫➡️🔋',
    }

UI_SCREEN_NAV_TO_LAUNDRY = {
        'title':'Yes Sr 🫡', 
        'subtitle':'Where are my pants?',
    }

UI_SCREEN_LOOK_FOR_PANTS = {
        'title':'Wait... 🤔', 
        'subtitle':'I don\'t use pants! 🤯',
    }

UI_SCREEN_COME_BACK_FROM_LAUNDRY = {
        'title':'Coming back', 
        'subtitle':'Naked 😳',
        'show_loader':False,
    }

UI_SCREEN_END = {
        'title':'Thanks!', 
        'subtitle':'Don\'t forget to subscribe and like 😉',
        'show_loader':False,
    }

UI_SCREEN_FAILED = {
        'title':'Something went wrong 💢', 
        'show_loader':False,
    }

# SELECTORS

UI_SELECTOR_WHERE_TO_GO = {
        'title': 'Where do you want me to go?', 
        'show_back_button': False, 
        'data': [
                {'id': 1, 'name': '🔪 Kitchen 🔪'}, 
                {'id': 2, 'name': '🛏 Bedroom 🛏'}, 
                {'id': 3, 'name': '🧦 Laundry 🧦'},
                {'id': 0, 'name': '❌ Finish App ❌'},
            ]
    }

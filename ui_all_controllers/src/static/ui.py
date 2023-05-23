#GENERAL

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
    }

# SOUND

UI_SOUND_MAIN_DISPLAY = {
        'title': 'You would like to:', 
        'show_back_button': False, 
        'data': [
                {'id': 1, 'name': '🔊 Play a predefined sound 🔊'}, 
                {'id': 2, 'name': '🎶 Play a custom sound 🎶'}, 
                {'id': 3, 'name': '🎙 Record a sound 🎙'},
                {'id': 3, 'name': '📢 Play a pre-recorded sound 📢'},
            ]
    }

UI_SOUND_PLAY_PREDEFINED = {
        'title': '🔊 Play a predefined sound 🔊', 
        'show_back_button': True, 
        'data': []
    }
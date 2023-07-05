from src.static.app_errors import *


# The first state is always the initial one
STATES = [
        'LOCALIZING',
        'NAV_TO_HOME',
        'IDLE',
        'TEMPERATURE',
        'KITCHEN',
        'BEDROOM',
        'LAUNDRY',
        'END',
    ]


# First state of FSM, if not defined, the FSM starts in the first element of
# the STATES list
INITIAL_STATE = 'LOCALIZING'


# If the FSM falls into one of these states, the execution finishes.
END_STATES = [
    'END',
]


# If one of the states takes more than an especified time, it aborts.
# Format: 'STATE': (<timeout>, <error_tuple>)
STATES_TIMEOUTS = {
    'LOCALIZING' : (10.0, APPERR_COULD_NOT_LOCALIZE),
}

from raya.tools.fsm import FSM

class TemperatureFSM(FSM):
    def __init__(self, *args, **kwarg):
        super().__init__(*args, **kwarg)

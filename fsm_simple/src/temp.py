import inspect

class MyClass:
    def __init__(self) -> None:
        self.name = 'hello'
        self.my_method2 = MyClass2()
        

class MyClass2:
    def __init__(self) -> None:
        self.app = get_caller()
        self.app.name = 'adios'


def get_caller() -> MyClass:
    # Get the caller frame
    caller_frame = inspect.currentframe().f_back.f_back
    return caller_frame.f_locals['self']

# Example usage:
obj = MyClass()
print(obj.name)
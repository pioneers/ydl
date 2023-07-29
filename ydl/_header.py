import inspect
from typing import Tuple

def header(channel, name):
    """
    Decorator that turns a regular function into a "header function". The
    header function calls the original function (so it can do input validation),
    then returns a message in this format:
    (channel, name, args)
    where args is a dictionary of the arguments
    """
    def make_header(func):
        parameters = inspect.signature(func).parameters
        arg_names = list(parameters.keys())
        default_params = {name: p.default for name, p in parameters.items()}

        def header_func(*args, **kwargs):
            func(*args, **kwargs)
            args_dict = default_params.copy()
            args_dict.update(zip(arg_names, args))
            args_dict.update(kwargs)
            return (channel, name, args_dict)

        header_func.ydl_channel = channel
        header_func.ydl_name = name
        header_func.ydl_arg_names = arg_names
        return header_func
    return make_header



class Handler():
    """
    A handler object is meant to store a bunch of functions,
    then call the corresponding function whenever a header is received
    """
    def __init__(self):
        self.mapping = {}

    def on(self, header_fn):
        """
        This decorator annotates a function that the handler should call whenever
        the given header is received. The original function is returned 
        by the decorator, so a function can be annotated multiple times.
        """
        def add_function(handling_fn):
            assert header_fn.ydl_name not in self.mapping, "duplicate header"

            header_params = header_fn.ydl_arg_names
            handle_params = list(inspect.signature(handling_fn).parameters.keys())
            assert header_params == handle_params, "Header has params " + \
                f"{header_params} but handler has params {handle_params}"

            self.mapping[header_fn.ydl_name] = handling_fn
            return handling_fn

        return add_function

    def can_handle(self, message: Tuple) -> bool:
        """
        Returns True if the message is well-formed, and there exists a 
        corresponding function for the handler to call.
        """
        return len(message) == 3 and \
                isinstance(message[1], str) and \
                isinstance(message[2], dict) and \
                message[1] in self.mapping

    def handle(self, message: Tuple) -> Tuple:
        """
        If the message is well-formed and an applicable function exists for the
        given message, calls that function and returns a single-element tuple 
        `(result,)`, where `result` is the return value of the function.
        Otherwise, returns an empty tuple. Note that `(result,)` is truthy and
        an empty tuple is falsy.
        """
        if self.can_handle(message):
            return (self.mapping.get(message[1])(**message[2]),)
        return ()

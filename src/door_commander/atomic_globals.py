import inspect
import traceback

#from icecream import ic


class AtomicGlobals:
    """unsets new global variables when exceptions occur. does not reset variables' values, nor mutable variables' contents """
    def __init__(self):
        self.globals = None
        self.original_keys = None
        self.exc_info = None
        self.removed_keys = None
    def __enter__(self):
        if self.globals is not None:
            raise Exception("This context can be reused, but is not reentrant.")
        self.globals = inspect.stack()[1].frame.f_globals
        self.original_keys = set(self.globals.keys())
        self.exc_info = None
        self.removed_keys = None
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.exc_info = (exc_type, exc_val, exc_tb,)
            current_keys = set(self.globals.keys())
            self.removed_keys = current_keys.difference(self.original_keys)
            #ic(self.original_keys, current_keys,self.removed_keys)
            if self.removed_keys:
                for key in self.removed_keys:
                    del self.globals[key]
        self.globals = None
        self.original_keys = None
        return True # suppress exceptions
    def __bool__(self):
        return self.exc_info is None
    def __str__(self):
        if self.globals is not None:
            return "<Atomic Global Variable Change (in progress>)"
        elif self.exc_info is None:
            return "<Atomic Global Variable Change (successful)"
        else:
            return "".join(traceback.format_exception(*self.exc_info))
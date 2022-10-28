class CallbackExecutor:
    def __init__(self, callback, *args):
        self.callback = callback
        self.args = args

    def execute(self):
        self.callback(*self.args)

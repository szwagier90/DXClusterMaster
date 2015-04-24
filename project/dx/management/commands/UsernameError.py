class UsernameError(ValueError):
    def __init__(self, arg):
        self.args = arg

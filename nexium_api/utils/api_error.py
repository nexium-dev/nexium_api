class ApiError(Exception):
    name: str = 'api_error'
    message: str = 'An error occurred'

    def __init__(self, message: str = None, **kwargs):
        if message:
            self.message = message

        self.class_name = self.__class__.__name__
        self.data = kwargs

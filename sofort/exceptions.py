class UnauthorizedError(Exception):
    pass

class RequestErrors(Exception):
    def __init__(self, response):
        super(RequestErrors, self).__init__('Request errors')
        self.errors = [RequestError(error) for error in response.error]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '; '.join([str(e) for e in self.errors])

class RequestError(Exception):
    def __init__(self, error_data):
        self.id = error_data.code
        self.message = error_data.message
        self.field = getattr(error_data, 'field', None)

    def __repr__(self):
        return self.code

    def __str__(self):
        result = str(self.message)
        if not self.field is None:
            result = '{}: {}'.format(self.field, result)
        return result

class UnauthorizedError(Exception):
    pass


class RequestErrors(Exception):
    def __init__(self, errors):
        super(RequestErrors, self).__init__('Request errors')
        self.errors = errors

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '; '.join([str(error) for error in self.errors])


class RequestError(Exception):
    def __init__(self, code, message, field=''):
        self.code = code
        self.message = message
        self.field = field

    def __repr__(self):
        return self.code

    def __str__(self):
        result = str(self.message)
        if self.field is not None:
            result = '{}: {}'.format(self.field, result)
        return result


class SofortWarning(Warning):
    def __init__(self, code, message, field=''):
        self.code = code
        self.message = message
        self.field = field

    def __repr__(self):
        return "[{0.code}] {0.field}: {0.message}".format(self)

    def __str__(self):
        return repr(self)

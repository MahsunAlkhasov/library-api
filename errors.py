class LibraryError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


def raise_error(message, status):
    return LibraryError(message, status)


def bad_request(message):
    return raise_error(message, 400)


def not_found(message):
    return raise_error(message, 404)


def conflict(message):
    return raise_error(message, 409)

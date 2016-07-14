"""
    Decorator definitions file
"""


def chatty_command(command=""):
    """

    :return: Print exception to stdout

    """

    def real_decorator(function):
        def wrapper(*args, **kw):
            try:
                function(*args, **kw)
            except Exception as e:
                print command, e, e.message

        return wrapper

    return real_decorator

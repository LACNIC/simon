"""
    Decorator definitions file
"""
import logging


def chatty_command(command=""):
    """

    :return: Print exception to stdout

    """

    def real_decorator(function):
        def wrapper(*args, **kw):
            try:
                function(*args, **kw)
            except Exception as e:
                logging.error("Command: %s \n Excepption thrown: %s \n Exception message: %s" % (command, e, e.message))

        return wrapper

    return real_decorator

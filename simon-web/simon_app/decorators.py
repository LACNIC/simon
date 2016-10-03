"""
    Decorator definitions file
"""
import logging
from simon_app.models.management import ProbeApiAudit


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


def probeapi(command="Default ProbeAPI Command"):
    """
    :return: ProbeAPI audit decorator

    """

    def real_decorator(function):
        def wrapper(*args, **kw):
            ca = ProbeApiAudit(command=command, status=True)
            try:
                results = function(*args, **kw)

                n = len(results)
                ca.count = n
                ca.description = "%d results saved." % n
            except Exception as e:
                logging.error("Command: %s \n Excepption thrown: %s \n Exception message: %s" % (command, e, e.message))
                ca.description = "Failed."
                ca.status = False
            finally:
                ca.save()

        return wrapper

    return real_decorator

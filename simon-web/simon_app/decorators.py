"""
    Decorator definitions file
"""
import logging
from datadog import statsd
from simon_project import settings
from simon_app.models.management import ProbeApiAudit


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


def timed(name=''):
    """
        Wrapper decorator around datadog's *statsd.timed* decorator
        :param function: function to be timed
        :return:
    """

    def real_decorator(function):

        view = ''
        if name == '':
            view = function.__name__
        else:
            view = name

        @statsd.timed('timed', tags=['view:' + view] + settings.DATADOG_DEFAULT_TAGS)
        def wrapper(*args, **kw):
            return function(*args, **kw)

        return wrapper

    return real_decorator


def chatty_command(command=""):
    """
    :return: Print exception to stdout

    """

    def real_decorator(function):
        def wrapper(*args, **kw):
            try:
                function(*args, **kw)
            except Exception as e:
                logging.error("Command: %s \n Exception thrown: %s \n Exception message: %s" % (command, e, e.message))

        return wrapper

    return real_decorator

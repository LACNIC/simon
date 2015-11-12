from simon_app.mailing import send_mail

"""
    Decorator definitions file
"""

from simon_app.mailing import *

def command(command=""):
    def decorator(function_to_decorate):
        def wrapper(*args, **kw):

            print "ANTES"

            # Calling your function
            output = function_to_decorate(*args, **kw)
            print "INMEDIATAMENTE DESPUES"
            print output
            send_mail_on_command_failed(command=command)

            print "DESPUES"

            return output
        return wrapper
    return decorator
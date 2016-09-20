import logging


class SimonLogger(logging.Logger):
    """
        SimonLogger overrides the default logging behaviour.
    """
    def _log(self, level, msg, *args, **kwargs):
        msg = unicode(msg)
        return logging.Logger._log(self, level, msg, *args, **kwargs)

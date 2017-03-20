from django import template
from datetime import datetime
from simon_app.reportes import GMTUY
import operator

"""
    Module that holds the Simon
"""

register = template.Library()


@register.filter(name="substract")
def substract(value, arg):
    """
        Substract
    """
    return value - arg


@register.filter(name="divide")
def divide(value, arg):
    """
        Float division
    """
    return float(value) / float(arg)


@register.filter(name="percentage")
def percentage(value, arg):
    """
        Percentage
    """
    return 100.0 * divide(value, arg)


@register.filter(name="unit_shortener")
def unit_shortener(value):
    """
        Unit converter
    """

    try:
        int(value)
        float(value)
    except:
        return "N/A"

    K = 1000
    M = K * K
    G = K * M
    T = K * G

    if value > T:
        return "%.1f %s" % (1.0 * value / T, 'T')
    if value > G:
        return "%.1f %s" % (1.0 * value / G, 'G')
    if value > M:
        return "%.1f %s" % (1.0 * value / M, 'M')
    if value > K:
        return "%.1f %s" % (1.0 * value / K, 'K')
    return value


@register.filter(name="time_since")
def time_since(value):
    """
    :param now:
    :return:
    """
    td = datetime.now(GMTUY()) - value
    if td.seconds > 3600:
        mins = "%.0f minutos" % ((td.seconds % 3600) / 60)
        horas = "%.0f %s" % (td.seconds / 3600, "horas" if td.seconds / 3600 > 1 else "hora")
        return "%s %s" % (horas, mins)
    elif td.seconds > 60:
        return "%.0f minutos" % (td.seconds / 60)
    else:
        return "%.0f segundos" % td.seconds


@register.filter(name="max")
def max_(value, arg):
    """
    :param value:
    :param arg:
    :return:
    """
    if arg == 'v6_rate':
        return str(max([v.v6_rate for v in value]))
    return "%s %s" % (value, arg)


@register.filter(name="get_by_attribute")
def get_by_attribute(objects, raw_args):

    print raw_args

    key, value = raw_args.split(' ')

    print key, value

    func = operator.attrgetter(key)

    for o in objects:
        if func(o) == value:
            return o

    class Object():
        pass

    a = Object()
    setattr(a, key, 0)
    return a


@register.filter(name="get_attribute")
def get_attribute(object, attr):
    func = operator.attrgetter(attr)
    return func(object)

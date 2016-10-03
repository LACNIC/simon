from django import template
from datetime import datetime
from simon_app.reportes import GMTUY

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

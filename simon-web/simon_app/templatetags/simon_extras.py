from django import template

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

from django import template

register = template.Library()

@register.filter
def absolutely(value):
    """
    Get the absolute value for "value".  This template tag is a wrapper for
    pythons "abs(...)" method.

    Usage:

    >>> absolute(-5)
    5
    """
    try:
        return abs(value)
    except:
        return value
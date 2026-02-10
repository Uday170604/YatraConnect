from django import template

register = template.Library()

@register.filter
def eq(value, arg):
    return str(value) == str(arg)

from django import template

register = template.Library()

@register.filter
def dict_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter
def slice_months(value):
    return value.split(',')

@register.filter
def split_csv(value):
    return [int(x) for x in value.split(',')]

@register.filter
def make_list(value):
    return list(value)

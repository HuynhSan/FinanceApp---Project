from django import template

register = template.Library()

@register.simple_tag
def month_range():
    return range(1, 13)

@register.simple_tag
def year_range(start=2020, end=2030):
    return range(start, end + 1)
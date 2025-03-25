from django import template
from ..models import Roster

register = template.Library()

@register.filter
def get_roster(rosters, staff_id_day):
    staff_id, day = staff_id_day.split('_')
    return next((r for r in rosters if r.staff.id == int(staff_id) and r.day == day), None)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
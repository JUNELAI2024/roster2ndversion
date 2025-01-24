from django import template

register = template.Library()

@register.filter
def get_roster(rosters, staff_id, day):
    # 实现你的逻辑
    return next((r for r in rosters if r.staff.id == staff_id and r.day == day), None)
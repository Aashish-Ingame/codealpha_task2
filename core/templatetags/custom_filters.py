from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name="timesince_short")
def timesince_short(value):
    """
    Returns a compact human-readable time difference:
      < 1 min  → "just now"
      < 1 hr   → "Xm"
      < 1 day  → "Xh"
      < 7 days → "Xd"
      < 30d    → "Xw"
      else     → "Mon DD" (e.g. "Jun 5")
    """
    if not value:
        return ""
    try:
        now = timezone.now()
        diff = now - value
        total_seconds = int(diff.total_seconds())

        if total_seconds < 60:
            return "just now"
        elif total_seconds < 3_600:
            return f"{total_seconds // 60}m"
        elif total_seconds < 86_400:
            return f"{total_seconds // 3_600}h"
        elif total_seconds < 604_800:
            return f"{diff.days}d"
        elif total_seconds < 2_592_000:
            return f"{diff.days // 7}w"
        else:
            return value.strftime("%b %-d") if hasattr(value, "strftime") else str(value)
    except (TypeError, ValueError, AttributeError):
        return str(value)

from django import template

from survey.models import Month

from datetime import date

register = template.Library()

@register.inclusion_tag('survey/_next_wr_day.html')
def wr_day():
    try:
        current_wr_day = Month.objects.get(open_checkin__lte=date.today(), close_checkin__gte=date.today())
        return {
            'type': 'current_wr_day',
            'date': current_wr_day.wr_day.strftime('%A, %B %d, %Y'),
            'open': current_wr_day.open_checkin.strftime('%A, %B %d, %Y'),
            'close': current_wr_day.close_checkin.strftime('%A, %B %d, %Y'),
        }
    except Month.DoesNotExist:
        try:
            next_wr_day = Month.objects.filter(open_checkin__gt=date.today()).order_by('wr_day')[0]
            return {
                'type': 'next_wr_day',
                'date': next_wr_day.wr_day.strftime('%A, %B %d, %Y'),
                'open': next_wr_day.open_checkin.strftime('%A, %B %d, %Y'),
                'close': next_wr_day.close_checkin.strftime('%A, %B %d, %Y'),
            }
        except IndexError:
            return

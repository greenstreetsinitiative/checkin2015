from survey.models import Month
from datetime import date

# round stored values to 3 decimal places for
# better human readability of the data dumps
def sanely_rounded(float):
    return round(float, 3)

def current_month():
    return Month.objects.get(open_checkin__lte=date.today(), close_checkin__gte=date.today())

def next_month():
    return Month.objects.filter(open_checkin__gt=date.today()).order_by('wr_day')[0]

def current_or_next_month():
    if current_month():
        return current_month()
    elif next_month():
        return next_month()
    else:
        return None

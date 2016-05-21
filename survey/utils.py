import datetime

# round stored values to 3 decimal places for
# better human readability of the data dumps
def sanely_rounded(float):
    return round(float, 3)

def this_month():
    # lets the checkin be open at the time of this function being invoked.
    if current_month():
        return current_month()
    else:
        from survey.models import Month
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        tomorrow = now + datetime.timedelta(days=1)
        return Month.objects.create(wr_day=now, open_checkin=yesterday, close_checkin=tomorrow)

def current_month():
    from survey.models import Month
    try:
        return Month.objects.get(open_checkin__lte=datetime.date.today(), close_checkin__gte=datetime.date.today())
    except:
        return False

def next_month():
    from survey.models import Month
    try:
        return Month.objects.filter(open_checkin__gt=datetime.date.today()).order_by('wr_day')[0]
    except:
        return False

def current_or_next_month():
    if current_month():
        return current_month()
    elif next_month():
        return next_month()
    else:
        return None

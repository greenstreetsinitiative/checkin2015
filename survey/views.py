from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# from django.forms.models import inlineformset_factory

from survey.models import Commutersurvey, Employer, Leg, Month
from survey.forms import CommuterForm, ExtraCommuterForm
from survey.forms import MakeLegs_NormalTW, MakeLegs_NormalFW, MakeLegs_WRTW, MakeLegs_WRFW


import json
import mandrill
from datetime import date

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def add_checkin(request):

    try:
        wr_day = Month.objects.get(open_checkin__lte=date.today(), close_checkin__gte=date.today())
    except Month.DoesNotExist:
        return redirect('/')

    if request.method == 'POST':
        commute_form = CommuterForm(request.POST)
        extra_commute_form = ExtraCommuterForm(request.POST)
        leg_formset_NormalTW = MakeLegs_NormalTW(request.POST, instance=Commutersurvey(), prefix='ntw')
        leg_formset_NormalFW = MakeLegs_NormalFW(request.POST, instance=Commutersurvey(), prefix='nfw')
        leg_formset_WRTW = MakeLegs_WRTW(request.POST, instance=Commutersurvey(), prefix='wtw')
        leg_formset_WRFW = MakeLegs_WRFW(request.POST, instance=Commutersurvey(), prefix='wfw')

        if commute_form.is_valid():
            commutersurvey = commute_form.save(commit=False)
            leg_formset_NormalTW = MakeLegs_NormalTW(request.POST, instance=commutersurvey, prefix='ntw')
            leg_formset_NormalFW = MakeLegs_NormalFW(request.POST, instance=commutersurvey, prefix='nfw')
            leg_formset_WRTW = MakeLegs_WRTW(request.POST, instance=commutersurvey, prefix='wtw')
            leg_formset_WRFW = MakeLegs_WRFW(request.POST, instance=commutersurvey, prefix='wfw')

            if leg_formset_NormalTW.is_valid() and leg_formset_NormalFW.is_valid() and leg_formset_WRTW.is_valid() and leg_formset_WRFW.is_valid():
                commutersurvey.wr_day_month = wr_day
                commutersurvey.email = commute_form.cleaned_data['email']
                commutersurvey.employer = commute_form.cleaned_data['employer']
                commutersurvey.team = commute_form.cleaned_data['team']

                if extra_commute_form.is_valid():
                    commutersurvey.share = extra_commute_form.cleaned_data['share']
                    commutersurvey.comments = extra_commute_form.cleaned_data['comments']

                commutersurvey.save()

                leg_formset_NormalTW.save()
                leg_formset_NormalFW.save()
                leg_formset_WRTW.save()
                leg_formset_WRFW.save()

                # very simple email sending - replace using Mandrill API later
                name = commutersurvey.name or 'Supporter'
                subject = 'Walk/Ride Day ' + commutersurvey.wr_day_month.month + ' Checkin'
                message_html = '<p>Dear ' + name +',</p><p>Thank you for checking in your Walk/Ride Day commute! This email confirms your participation in ' + commutersurvey.wr_day_month.month + '\'s Walk/Ride Day! Feel free to show it to our <a href="http://checkin-greenstreets.rhcloud.com/retail" style="color: #2ba6cb;text-decoration: none;">Retail Partners</a> to take advantage of their offers of freebies, discounts, and other goodies!</p><p>Now <a href="http://checkin2015-greenstreets.rhcloud.com/leaderboard/" style="color: #2ba6cb;text-decoration: none;">CLICK HERE</a> to see how your company is doing in the Corporate Challenge! Share with your friends and colleagues!</p><p>Thank you for being involved! Remember to check-in for next month\'s Walk/Ride Day.</p><p>Warmly,<br><span style="color:#006600;font-weight:bold;">Janie Katz-Christy, Director <br>Green Streets Initiative<br> <span class="mobile_link">617-299-1872 (office)</p><p>Share with your friends and colleagues! <a href="http://checkin.gogreenstreets.org" style="color: #2ba6cb;text-decoration: none;">Make sure they get a chance to check in</p>'
                message_plain = 'Dear Supporter, Thank you for checking in your Walk/Ride Day commute! This email confirms your participation in ' + commutersurvey.wr_day_month.month + '\'s Walk/Ride Day! Feel free to show it to our Retail Partners to take advantage of their offers of freebies, discounts, and other goodies! Thank you for being involved! Remember to check-in for next month\'s Walk/Ride Day. Warmly, Green Streets Initiative'
                recipient_list = [commutersurvey.email,]
                from_email = 'checkin@gogreenstreets.org'
                try:
                    send_mail(subject, message_plain, from_email, recipient_list, html_message=message_html)

                return HttpResponseRedirect('complete/')
            pass
     

    else:
        commute_form = CommuterForm()
        extra_commute_form = ExtraCommuterForm()

        leg_formset_NormalTW = MakeLegs_NormalTW(instance=Commutersurvey(), prefix='ntw')
        leg_formset_NormalFW = MakeLegs_NormalFW(instance=Commutersurvey(), prefix='nfw')
        leg_formset_WRTW = MakeLegs_WRTW(instance=Commutersurvey(), prefix='wtw')
        leg_formset_WRFW = MakeLegs_WRFW(instance=Commutersurvey(), prefix='wfw')

    return render(request, "survey/new_checkin.html", { 'wr_day': wr_day, 'form': commute_form, 'extra_form': extra_commute_form, 'NormalTW_formset': leg_formset_NormalTW, 'NormalFW_formset': leg_formset_NormalFW, 'WRTW_formset': leg_formset_WRTW, 'WRFW_formset': leg_formset_WRFW })

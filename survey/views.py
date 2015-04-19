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

def send_email(template, template_content, message):
    try:
        mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
        mandrill_client.messages.send_template(template_name=template, template_content=template_content, message=message)
    except mandrill.Error, e:
        pass
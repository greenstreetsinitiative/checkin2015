from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# from django.forms.models import inlineformset_factory


from survey.models import Commutersurvey, Employer, Leg, Month
from survey.forms import CommuterForm, ExtraCommuterForm
from survey.forms import MakeLegs_NormalTW, MakeLegs_NormalFW, MakeLegs_WRTW, MakeLegs_WRFW
from survey.forms import NormalFromWorkSameAsAboveForm, WalkRideFromWorkSameAsAboveForm, NormalIdenticalToWalkrideForm
#former code in this block was:
#from survey.models import Commutersurvey, Employer, Leg, Month
#from survey.forms import CommuterForm, ExtraCommuterForm
#from survey.forms import MakeLegs_NormalTW, MakeLegs_NormalFW, MakeLegs_WRTW, MakeLegs_WRFW
#so, just added the normalfromwork etc line

import json
import mandrill
from datetime import date


from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect


def add_checkin(request):

    try:
        wr_day = Month.objects.get(open_checkin__lte=date.today(),
                                   close_checkin__gte=date.today())
    except Month.DoesNotExist:
        return redirect('/')

    if request.method == 'POST':
        # send the filled out forms in!
        # if the forms turn out to be not valid, they will still retain
        # the form data from the POST request this way.
        commute_form = CommuterForm(request.POST)
        extra_commute_form = ExtraCommuterForm(request.POST)

        normal_copy = NormalFromWorkSameAsAboveForm(request.POST)
        wrday_copy = WalkRideFromWorkSameAsAboveForm(request.POST)
        commute_copy = NormalIdenticalToWalkrideForm(request.POST)

        # Set these all at once here, simply based on user input.
        # If we re-render the form this ensures at least all the
        # leg forms have data from request.POST, regardless of scenario.
        leg_formset_WRTW = MakeLegs_WRTW(
            request.POST, instance=Commutersurvey(), prefix='wtw')
        leg_formset_WRFW = MakeLegs_WRFW(
            request.POST, instance=Commutersurvey(), prefix='wfw')
        leg_formset_NormalTW = MakeLegs_NormalTW(
            request.POST, instance=Commutersurvey(), prefix='ntw')
        leg_formset_NormalFW = MakeLegs_NormalFW(
            request.POST, instance=Commutersurvey(), prefix='nfw')

        # if the main form is correct
        if commute_form.is_valid():
            commutersurvey = commute_form.save(commit=False)
            commutersurvey.wr_day_month = wr_day
            commutersurvey.email = commute_form.cleaned_data['email']
            commutersurvey.employer = commute_form.cleaned_data['employer']
            if 'team' in commute_form.cleaned_data:
                commutersurvey.team = commute_form.cleaned_data['team']

            extra_commute_form.is_valid() # creates cleaned_data
            if 'share' in extra_commute_form.cleaned_data:
                commutersurvey.share = extra_commute_form.cleaned_data['share']
            commutersurvey.comments = extra_commute_form.cleaned_data['comments']

            # write form responses to cookie
            for attr in ['name', 'email', 'home_address', 'work_address']:
                # TODO: include employer and team
                if attr in commute_form.cleaned_data:
                    request.session[attr] = commute_form.cleaned_data[attr]
            for attr in ['share', 'comments', 'volunteer']:
                if attr in extra_commute_form.cleaned_data:
                    request.session[attr] = extra_commute_form.cleaned_data[attr]

            #################
            # SAVE THE LEGS #
            #################
            # NEW APPROACH: ONE LARGE SET OF NESTED IFS TO RULE THEM ALL!
            # (AS A REPLACEMENT FOR THE FORMER FOUR-STEP RADIO-BUTTON PROCESS WHICH
            # WASN'T WORKING CLEANLY IN THE SAMPLE CHECKIN CODE).
            # FOR NOW HAD TO UNPACK THE FORMER IF-THEN PROCESS, WHICH WAS
            # MANY LESS LINES OF CODE BUT ALSO WAS NOT WORKING FOR SEVERAL SCENARIOS
            # AND COULD NOT BE DEBUGGED.
            # WE CAN FIND A WAY TO CONDENSE THIS DOWN TO LESS LINES OF CODE, AS SOON AS WE HAVE TIME.
            all_legs_valid = True
            leg_formset_WRTW = MakeLegs_WRTW(
                 request.POST, instance=commutersurvey, prefix='wtw')
            # validate wtw input
            for form in leg_formset_WRTW:
                if not form.is_valid():
                    all_legs_valid = False
            if all_legs_valid:
                # so far, the w/r legs to work are valid
                if request.POST['normal_same_as_reverse'] == 'True':
                    if request.POST['normal_same_as_walkride'] == 'True':
                        if request.POST['walkride_same_as_reverse'] == 'True':
                            # set w/r legs from work = w/r legs to work
                            leg_formset_WRFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_WRFW:
                                leg = form.save(commit=False)
                                leg.direction = 'fw'
                            # set normal legs to work = w/r legs to work
                            leg_formset_NormalTW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_NormalTW:
                                leg = form.save(commit=False)
                                leg.day = 'n'
                            # set normal legs from work = w/r legs to work
                            leg_formset_NormalFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_NormalFW:
                                leg = form.save(commit=False)
                                leg.day = 'n'
                                leg.direction = 'fw'
                        else:
                            # IF THE WALKRIDE-SAME BUTTON IS "NO", OBTAIN USER INPUT FOR THAT SECTION
                            leg_formset_WRFW = MakeLegs_WRFW(
                                request.POST, instance=commutersurvey, prefix='wfw')
                            # validate wfw input
                            for form in leg_formset_WRFW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            if all_legs_valid:
                                # set normal legs to work = w/r legs to work
                                leg_formset_NormalTW = MakeLegs_WRTW(
                                    request.POST, instance=commutersurvey, prefix='wtw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalTW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                # set normal legs from work = w/r legs from work
                                leg_formset_NormalFW = MakeLegs_WRFW(
                                    request.POST, instance=commutersurvey, prefix='wfw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalFW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                    leg.direction = 'fw'
                            else:
                                # w/r from work is NOT VALID but needs to be.
                                pass
                    else:
                        if request.POST['walkride_same_as_reverse'] == 'True':
                            # set w/r legs from work = w/r legs to work
                            leg_formset_WRFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_WRFW:
                                leg = form.save(commit=False)
                                leg.direction = 'fw'
                            # set normal legs to work = user input
                            leg_formset_NormalTW = MakeLegs_NormalTW(
                                request.POST, instance=commutersurvey, prefix='ntw')
                            # validate ntw input
                            for form in leg_formset_NormalTW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            if all_legs_valid:
                                # set normal legs from work = w/r legs to work
                                leg_formset_NormalFW = MakeLegs_NormalTW(
                                    request.POST, instance=commutersurvey, prefix='ntw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalFW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                    leg.direction = 'fw'
                            else:
                                # normal to work is NOT VALID but needs to be.
                                pass
                        else:
                            # IF THE WALKRIDE-SAME BUTTON IS "NO", OBTAIN USER INPUT FOR THAT SECTION
                            leg_formset_WRFW = MakeLegs_WRFW(
                                 request.POST, instance=commutersurvey, prefix='wfw')
                            # validate wfw input
                            for form in leg_formset_WRFW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            # set normal legs to work = user input
                            leg_formset_NormalTW = MakeLegs_NormalTW(
                                 request.POST, instance=commutersurvey, prefix='ntw')
                            # validate ntw input
                            for form in leg_formset_NormalTW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            if all_legs_valid:
                                # set normal legs from work = normal to work
                                leg_formset_NormalFW = MakeLegs_NormalTW(
                                    request.POST, instance=commutersurvey, prefix='ntw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalFW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                    leg.direction = 'fw'
                            else:
                                # normal to work OR w/r from work is NOT VALID and needs to be
                                pass
                else:
                    if request.POST['normal_same_as_walkride'] == 'True':
                        if request.POST['walkride_same_as_reverse'] == 'True':
                            # set w/r legs from work = w/r legs to work
                            leg_formset_WRFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_WRFW:
                                leg = form.save(commit=False)
                                leg.direction = 'fw'
                            # set normal legs to work = w/r legs to work
                            leg_formset_NormalTW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_NormalTW:
                                leg = form.save(commit=False)
                                leg.day = 'n'
                            # set normal legs from work = w/r legs to work
                            leg_formset_NormalFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_NormalFW:
                                leg = form.save(commit=False)
                                leg.day = 'n'
                                leg.direction = 'fw'
                        else:
                            # IF THE WALKRIDE-SAME BUTTON IS "NO", OBTAIN USER INPUT FOR THAT SECTION
                            leg_formset_WRFW = MakeLegs_WRFW(
                                request.POST, instance=commutersurvey, prefix='wfw')
                            # validate wfw input
                            for form in leg_formset_WRFW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            if all_legs_valid:
                                # set normal legs to work = w/r legs to work
                                leg_formset_NormalTW = MakeLegs_WRTW(
                                    request.POST, instance=commutersurvey, prefix='wtw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalTW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                # set normal legs from work = w/r legs from work
                                leg_formset_NormalFW = MakeLegs_WRFW(
                                    request.POST, instance=commutersurvey, prefix='wfw')
                                # need to correct for the hidden fields
                                for form in leg_formset_NormalFW:
                                    leg = form.save(commit=False)
                                    leg.day = 'n'
                                    leg.direction = 'fw'
                            else:
                                # w/r from work is NOT VALID and needs to be
                                pass
                    else:
                        if request.POST['walkride_same_as_reverse'] == 'True':
                            # set w/r legs from work = w/r legs to work
                            leg_formset_WRFW = MakeLegs_WRTW(
                                request.POST, instance=commutersurvey, prefix='wtw')
                            # need to correct for the hidden fields
                            for form in leg_formset_WRFW:
                                leg = form.save(commit=False)
                                leg.direction = 'fw'
                            # set normal legs to work = user input
                            leg_formset_NormalTW = MakeLegs_NormalTW(
                                request.POST, instance=commutersurvey, prefix='ntw')
                            # validate ntw input
                            for form in leg_formset_NormalTW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            # set normal legs from work = user input
                            leg_formset_NormalFW = MakeLegs_NormalFW(
                                request.POST, instance=commutersurvey, prefix='nfw')
                            # validate nfw input
                            for form in leg_formset_NormalFW:
                                if not form.is_valid():
                                    all_legs_valid = False

                            if not all_legs_valid:
                                # normal TW or normal FW are NOT VALID and need to be
                                pass
                        else:
                            # IF THE WALKRIDE-SAME BUTTON IS "NO", OBTAIN USER INPUT FOR THAT SECTION
                            leg_formset_WRFW = MakeLegs_WRFW(
                                request.POST, instance=commutersurvey, prefix='wfw')
                            # validate wfw input
                            for form in leg_formset_WRFW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            # set normal legs to work = user input
                            leg_formset_NormalTW = MakeLegs_NormalTW(
                                request.POST, instance=commutersurvey, prefix='ntw')
                            # validate ntw input
                            for form in leg_formset_NormalTW:
                                if not form.is_valid():
                                    all_legs_valid = False
                            # set normal legs from work = user input
                            leg_formset_NormalFW = MakeLegs_NormalFW(
                                request.POST, instance=commutersurvey, prefix='nfw')
                            # validate nfw input
                            for form in leg_formset_NormalFW:
                                if not form.is_valid():
                                    all_legs_valid = False

                            if not all_legs_valid:
                                # something is NOT VALID and needs to be
                                pass


                # finally! we're good to go.
                if (all_legs_valid and
                    leg_formset_WRTW.is_valid() and
                    leg_formset_NormalTW.is_valid() and
                    leg_formset_NormalFW.is_valid() and
                    leg_formset_WRFW.is_valid()):

                    commutersurvey.save()
                    leg_formset_WRTW.save()
                    leg_formset_WRFW.save()
                    leg_formset_NormalTW.save()
                    leg_formset_NormalFW.save()
                    # very simple email sending - replace using Mandrill API later
                    name = commutersurvey.name or 'Supporter'
                    subject = ('Walk/Ride Day ' +
                               commutersurvey.wr_day_month.month + ' Checkin')
                    message_html = (
                        '<p>Dear {name},</p><p>Thank you for checking'
                        ' in your Walk/Ride Day commute! This email confirms your'
                        ' participation in {survey_date}\'s Walk/Ride Day! Feel '
                        'free to show it to our <a href="http://checkin'
                        '-greenstreets.rhcloud.com/retail" style="color:'
                        '#2ba6cb;text-decoration: none;">Retail Partners</a> '
                        'to take advantage of their offers of freebies, '
                        'discounts, and other goodies!</p><p>If you haven\'t already, <a href="http://'
                        'checkin2015-greenstreets.rhcloud.com/leaderboard/" '
                        'style="color: #2ba6cb;text-decoration: none;">CLICK HERE'
                        '</a> to see how your company did in the 2015 Corporate'
                        ' Challenge, which ended with the October Walk/Ride Day.</p>'
                        '<p>Thank you for being involved! Remember to check-in '
                        'for next month\'s Walk/Ride Day.</p><p>Warmly,<br>'
                        '<span style="color:#006600;font-weight:bold;">Janie Katz'
                        '-Christy, Director <br>Green Streets Initiative<br> '
                        '<span class="mobile_link">617-299-1872 (office)</p>'
                        '<p>Share with your friends and colleagues! '
                        '<a href="http://checkin.gogreenstreets.org" '
                        'style="color: #2ba6cb;text-decoration: none;">Make sure'
                        ' they get a chance to check in</p>'.format(
                            name=name,
                            survey_date=commutersurvey.wr_day_month.month))

                    message_plain = (
                        'Dear Supporter, Thank you for checking in '
                        'your Walk/Ride Day commute! This email confirms your'
                        ' participation in ' + commutersurvey.wr_day_month.month +
                        '\'s Walk/Ride Day! Feel free to show it to our Retail'
                        ' Partners to take advantage of their offers of freebies,'
                        ' discounts, and other goodies! Thank you for being'
                        ' involved! Remember to check-in for next month\'s Walk/Ride'
                        ' Day. Warmly, Green Streets Initiative')
                    recipient_list = [commutersurvey.email,]
                    from_email = 'checkin@gogreenstreets.org'
                    send_mail(subject, message_plain, from_email, recipient_list,
                              html_message=message_html, fail_silently=True)
                    return render_to_response(
                        'survey/thanks.html',
                        {
                            'person': commutersurvey.name,
                            'calories_burned': commutersurvey.calories_total,
                            'calorie_change': commutersurvey.calorie_change,
                            'carbon_savings': commutersurvey.carbon_savings,
                            'change_type': commutersurvey.change_type,
                        })
                else:
                    # it wasn't all valid
                    pass
            else:
                # w/r to work is NOT VALID but needs to be.
                pass
        else:
            pass

    else:
        # initialize forms with cookies
        initial_commute = {}
        initial_extra_commute = {}

        for attr in ['name', 'email', 'home_address', 'work_address']:
            if attr in request.session:
                initial_commute[attr] = request.session.get(attr)

        for attr in ['share', 'comments', 'volunteer']:
            if attr in request.session:
                initial_extra_commute[attr] = request.session.get(attr)

        commute_form = CommuterForm(initial=initial_commute)
        extra_commute_form = ExtraCommuterForm(initial=initial_extra_commute)

        # TODO: use request session to instantiate the formsets with initial=[{},{},{}...] for each formset

        leg_formset_NormalTW = MakeLegs_NormalTW(instance=Commutersurvey(), prefix='ntw')
        leg_formset_NormalFW = MakeLegs_NormalFW(instance=Commutersurvey(), prefix='nfw')
        leg_formset_WRTW = MakeLegs_WRTW(instance=Commutersurvey(), prefix='wtw')
        leg_formset_WRFW = MakeLegs_WRFW(instance=Commutersurvey(), prefix='wfw')

        normal_copy = NormalFromWorkSameAsAboveForm()
        wrday_copy = WalkRideFromWorkSameAsAboveForm()
        commute_copy = NormalIdenticalToWalkrideForm()

    return render(request, "survey/new_checkin.html",
                  {
                      'wr_day': wr_day,
                      'form': commute_form,
                      'extra_form': extra_commute_form,
                      'NormalTW_formset': leg_formset_NormalTW,
                      'NormalFW_formset': leg_formset_NormalFW,
                      'WRTW_formset': leg_formset_WRTW,
                      'WRFW_formset': leg_formset_WRFW,
                      'normal_copy': normal_copy,
                      'wrday_copy': wrday_copy,
                      'commute_copy': commute_copy,
                  })

#return render(request, "survey/new_checkin.html",
#                  {
#                      'wr_day': wr_day,
#                      'form': commute_form,
#                      'extra_form': extra_commute_form,
#                      'NormalTW_formset': leg_formset_NormalTW,
#                      'NormalFW_formset': leg_formset_NormalFW,
#                      'WRTW_formset': leg_formset_WRTW,
#                     'WRFW_formset': leg_formset_WRFW
#                  })

from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from survey.models import Commutersurvey, Employer, Leg, Month, Team
from survey.forms import CommuterForm, ExtraCommuterForm
from survey.forms import MakeLegs_NormalTW, MakeLegs_NormalFW, MakeLegs_WRTW, MakeLegs_WRFW
from survey.forms import NormalFromWorkSameAsAboveForm, WalkRideFromWorkSameAsAboveForm, NormalIdenticalToWalkrideForm
#former code in this block was:
#from survey.models import Commutersurvey, Employer, Leg, Month
#from survey.forms import CommuterForm, ExtraCommuterForm
#from survey.forms import MakeLegs_NormalTW, MakeLegs_NormalFW, MakeLegs_WRTW, MakeLegs_WRFW
#so, just added the normalfromwork etc line

import json
from datetime import date
import datetime
import requests

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

import base64

@csrf_exempt
def add_checkin(request):


    try:
        wr_day = Month.objects.get(open_checkin__lte=date.today(),
                                   close_checkin__gte=date.today())
    except Month.DoesNotExist:
        return redirect('/')

    if request.POST:
        # send the filled out forms in!
        # if the forms turn out to be not valid, they will still retain
        # the form data from the POST request this way.
        commute_form = CommuterForm(request.POST)
        extra_commute_form = ExtraCommuterForm(request.POST)

        normal_copy = NormalFromWorkSameAsAboveForm(request.POST)
        wrday_copy = WalkRideFromWorkSameAsAboveForm(request.POST)
        commute_copy = NormalIdenticalToWalkrideForm(request.POST)

        if not commute_form.is_valid():
            # instance = Commutersurvey()
            leg_formset_WRTW = MakeLegs_WRTW(
                request.POST, prefix='wtw')
            leg_formset_WRFW = MakeLegs_WRFW(
                request.POST, prefix='wfw')
            leg_formset_NormalTW = MakeLegs_NormalTW(
                request.POST, prefix='ntw')
            leg_formset_NormalFW = MakeLegs_NormalFW(
                request.POST, prefix='nfw')
        else:
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
                if attr in commute_form.cleaned_data:
                    request.session[attr] = commute_form.cleaned_data[attr]
            for attr in ['employer', 'team']:
                if attr in commute_form.cleaned_data:
                    if commute_form.cleaned_data[attr] is not None:
                        # import pdb; pdb.set_trace()
                        request.session[attr] = commute_form.cleaned_data[attr].id
            for attr in ['share', 'volunteer']:
                if attr in extra_commute_form.cleaned_data:
                    request.session[attr] = extra_commute_form.cleaned_data[attr]

            # This is just to generate cleaned_data. The radio button choices will be valid.
            wrday_copy.is_valid(); commute_copy.is_valid(); normal_copy.is_valid();
            request.session['walkride_same_as_reverse'] = str(wrday_copy.cleaned_data['walkride_same_as_reverse'])
            request.session['normal_same_as_walkride'] = str(commute_copy.cleaned_data['normal_same_as_walkride'])
            request.session['normal_same_as_reverse'] = str(normal_copy.cleaned_data['normal_same_as_reverse'])

            ##################################
            # SAVE THE LEGS WITH THE CHECKIN #
            ##################################
            leg_formset_WRTW = MakeLegs_WRTW(
                request.POST, instance=commutersurvey, prefix='wtw')
            leg_formset_WRFW = MakeLegs_WRFW(
                request.POST, instance=commutersurvey, prefix='wfw')
            leg_formset_NormalTW = MakeLegs_NormalTW(
                request.POST, instance=commutersurvey, prefix='ntw')
            leg_formset_NormalFW = MakeLegs_NormalFW(
                request.POST, instance=commutersurvey, prefix='nfw')

            if leg_formset_WRTW.is_valid() and leg_formset_WRFW.is_valid() and leg_formset_NormalTW.is_valid() and leg_formset_NormalFW.is_valid():
                commutersurvey.save()
                leg_formset_WRTW.save()
                leg_formset_WRFW.save()
                leg_formset_NormalTW.save()
                leg_formset_NormalFW.save()


                bikeTotal = 0
                runTotal = 0
                walkTotal = 0

                
                for form in leg_formset_WRTW:
                    if("Biking" in str(form.cleaned_data['mode'])):
                        bikeTotal += form.cleaned_data['duration']
                    if("Run" in str(form.cleaned_data['mode'])):
                        runTotal += form.cleaned_data['duration']
                    if("Walk" in str(form.cleaned_data['mode'])):
                        walkTotal += form.cleaned_data['duration']

                for form in leg_formset_WRFW:
                    if("Biking" in str(form.cleaned_data['mode'])):
                        bikeTotal += form.cleaned_data['duration']
                    if("Run" in str(form.cleaned_data['mode'])):
                        runTotal += form.cleaned_data['duration']
                    if("Walk" in str(form.cleaned_data['mode'])):
                        walkTotal += form.cleaned_data['duration']

                stravaDisplay = ''
                if 'strava_access_token' in request.session:
                    stravaDisplay = 'display'

                fitbitDisplay = ''
                if 'fitbit_name' in request.session:
                    fitbitDisplay = 'display'


                write_formset_cookies(request, leg_formset_WRTW, leg_formset_WRFW, leg_formset_NormalTW, leg_formset_NormalFW)
                send_email(commutersurvey)

                return render_to_response(
                    'survey/thanks.html',
                    {
                        'person': commutersurvey.name,
                        'calories_burned': commutersurvey.calories_total,
                        'calorie_change': commutersurvey.calorie_change,
                        'carbon_savings': commutersurvey.carbon_savings,
                        'change_type': commutersurvey.change_type,
                        'bike_total' : bikeTotal,
                        'run_total' : runTotal,
                        'walk_total' : walkTotal,
                        'strava_display' : stravaDisplay,
                        'fitbit_display' : fitbitDisplay,
                    },
                    context_instance=RequestContext(request))
            else:
                pass
    else:
        # initialize forms with cookies
        initial_commute = {}
        initial_extra_commute = {}

        for attr in ['name', 'email', 'home_address', 'work_address', 'employer', 'team']:
            if attr in request.session:
                initial_commute[attr] = request.session.get(attr)

        for attr in ['share', 'volunteer']:
            if attr in request.session:
                initial_extra_commute[attr] = request.session.get(attr)

        if 'employer' in request.session:
            id = request.session.get('employer')
            try:
                initial_commute['employer'] = Employer.objects.get(pk=id)
            except Employer.DoesNotExist:
                initial_commute['employer'] = ''
        if 'team' in request.session:
            teamid = request.session.get('team')
            if teamid:
                try:
                    initial_commute['team'] = Team.objects.get(pk=teamid)
                except Team.DoesNotExist:
                    initial_commute['team'] = ''

        commute_form = CommuterForm(initial=initial_commute)
        extra_commute_form = ExtraCommuterForm(initial=initial_extra_commute)

        # TODO: use request session to instantiate the formsets with initial=[{},{},{}...] for each formset

        leg_formset_NormalTW = MakeLegs_NormalTW(instance=Commutersurvey(), prefix='ntw')
        leg_formset_NormalFW = MakeLegs_NormalFW(instance=Commutersurvey(), prefix='nfw')
        leg_formset_WRTW = MakeLegs_WRTW(instance=Commutersurvey(), prefix='wtw')
        leg_formset_WRFW = MakeLegs_WRFW(instance=Commutersurvey(), prefix='wfw')

        if 'normal_same_as_reverse' in request.session:
            normal_copy = NormalFromWorkSameAsAboveForm(initial={'normal': request.session.get('normal_same_as_reverse')})
        else:
            normal_copy = NormalFromWorkSameAsAboveForm()

        if 'walkride_same_as_reverse' in request.session:
            wrday_copy = WalkRideFromWorkSameAsAboveForm(initial={'wr_day': request.session.get('walkride_same_as_reverse')})
        else:
            wrday_copy = WalkRideFromWorkSameAsAboveForm()

        if 'normal_same_as_walkride' in request.session:
            commute_copy = NormalIdenticalToWalkrideForm(initial={'commute': request.session.get('normal_same_as_walkride')})
        else:
            commute_copy = NormalIdenticalToWalkrideForm()


    fitbit_name = ''
    if 'fitbit_name' in request.session:
        fitbit_name = request.session['fitbit_name']

    strava_username = ''
    if 'strava_username' in request.session:
        strava_username = request.session['strava_username']

    # now just go ahead and render.
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
                      #'fullname': stravaDict['fullname'],
                      #'email': stravaDict['email'],
                      'strava_username': strava_username,
                      'fitbit_name': fitbit_name
                  })

def send_email(commutersurvey):
    name = commutersurvey.name or 'Supporter'
    subject = ('Walk/Ride Day ' +
               commutersurvey.wr_day_month.month + ' Checkin')
    message_html = (
        '<p>Dear {name},</p><p>Thank you for checking'
        ' in your Walk/Ride Day commute! This email confirms your'
        ' participation in {survey_date}\'s Walk/Ride Day! Feel '
        'free to show it to our <a href="http://checkinapp'
        '-greenstreets.rhcloud.com/retail" style="color:'
        '#2ba6cb;text-decoration: none;">Retail Partners</a> '
        'to take advantage of their offers of freebies, '
        'discounts, and other goodies!</p><p>To see how your '
        'company is ranked in the 2016 Walk/Ride Day CORPORATE '
        'CHALLENGE, <a href="http://'
        'checkinapp-greenstreets.rhcloud.com/leaderboard/2016" '
        'style="color: #2ba6cb;text-decoration: none;">click here'
        '</a>.</p>'
        '<p>Thank you for being involved! By checking in and '
        'sharing your commuting information, you are helping improve'
        ' the livability and health of our shared community. Please '
        'mark your calendar to remember to check-in for next '
        'month\'s Walk/Ride Day!</p><p>Warmly,<br>'
        '<span style="color:#006600;font-weight:bold;">Janie Katz'
        '-Christy, Director <br>Green Streets Initiative</span><br> '
        '<span class="mobile_link">617-299-1872 (office)</span></p>'
        '<p>Share with your friends and colleagues! '
        '<a href="http://checkinapp-greenstreets.rhcloud.com/" '
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

def write_formset_cookies(request, *args):
    # takes a list of formsets and writes them to the session
    for formset in args:
        for form in formset:
            for attr in form.cleaned_data:
                input_name = form.prefix + '-' + attr
                if attr in ['mode', 'checkin']:
                    request.session[input_name] = form.cleaned_data[attr].id
                else:
                    request.session[input_name] = form.cleaned_data[attr]

def stravaLogin(request):

    #fullname = ''
    #email = ''
    stravaUsername = ''
    stravaCode = request.GET.get('code', '')
    if 'code' in request.session and stravaCode == '':
        stravaCode =  request.session['code']
    if stravaCode != '':
        params = {'client_id':12852, 'client_secret':'cfa726430a012abbf44b73a4c24e04ede3a033b1', 'code':stravaCode}
        r = requests.post("https://www.strava.com/oauth/token", data=params)
        if r.status_code == 200:
            j = json.loads(r.text)
            request.session['strava_access_token'] = j['access_token']
            #request.session['code'] = stravaCode
            #fullname = j['athlete']['firstname'] + " " + j['athlete']['lastname']
            #email = j['athlete']['email']
            request.session['strava_username'] = j['athlete']['username']
        else:
            return redirect('logout_all')

    #return {'fullname' : fullname, 'email' : email, 'stravaUsername': stravaUsername, 'stravaCode': stravaCode }
    return redirect('commuterform')


def stravaupload(request, bikeTotal, runTotal, walkTotal):

    params = {'access_token': request.session['strava_access_token'], 'name':'GSI Walk/Ride Day Commute', 'type':'', 'start_date_local': datetime.datetime.now(), 'elapsed_time': 0 }

    bikeTotal = int(bikeTotal)
    runTotal = int(runTotal)
    walkTotal = int(walkTotal)

    #bikeTotal = int(request.session['strava_bike_total'])

    if bikeTotal > 0:
        params['type'] = 'Ride'
        params['elapsed_time'] = bikeTotal * 60
        params['name'] = 'GSI Walk/Ride Day Commute (Bike)'
        requests.post("https://www.strava.com/api/v3/activities", data=params)

    #runTotal = int(request.session['strava_run_total'])

    if runTotal > 0:
        params['type'] = 'Run'
        params['elapsed_time'] = runTotal * 60
        params['name'] = 'GSI Walk/Ride Day Commute (Run)'
        requests.post("https://www.strava.com/api/v3/activities", data=params)


    #walkTotal = int(request.session['strava_walk_total'])

    if walkTotal > 0:
        params['type'] = 'Walk'    
        params['elapsed_time'] = walkTotal * 60
        params['name'] = 'GSI Walk/Ride Day Commute (Walk)'
        requests.post("https://www.strava.com/api/v3/activities", data=params)


    return HttpResponse('<h1>Page was found</h1>')


def logoutSteps(request):
    #if 'code' in request.session:
    #    del request.session['code']

    if 'strava_username' in request.session:
        del request.session['strava_username']

    if 'strava_access_token' in request.session:
        del request.session['strava_access_token']

    if 'fitbit_name' in request.session:
        del request.session['fitbit_name']

    if 'fitbit_access_token' in request.session:
        del request.session['fitbit_access_token']

    if 'fitbit_user_id' in request.session:
        del request.session['fitbit_user_id']
        
    request.session.modified = True


def logout(request):
    logoutSteps(request)
    return redirect('commuterform')



def fitbitLogin(request):
    fullname = ''
    email = ''
    stravaUsername = ''
    fitbitCode = request.GET.get('code', '')
    
    #if 'code' in request.session and stravaCode == '':
    #    stravaCode =  request.session['code']
    #if stravaCode != '':
    params = {'client_id':'227S4M', 'code': fitbitCode, 'grant_type':'authorization_code', 'redirect_uri':'http://mysite.com:8000/fitbitLogin/'}

    encoded = "Basic " + str(base64.b64encode("227S4M:1b9ba7635ace55e7c106ffd1a8c72e40"))

    headers = {'Authorization': encoded, 'Content-Type': 'application/x-www-form-urlencoded' }


    r = requests.post("https://api.fitbit.com/oauth2/token", data=params, headers=headers)


    print(r.status_code)
    if r.status_code == 200:
        j = json.loads(r.text)
        #request.session['strava_access_token'] = j['access_token']
        #request.session['code'] = stravaCode
        #fullname = j['athlete']['firstname'] + " " + j['athlete']['lastname']
        #email = j['athlete']['email']
        #stravaUsername = j['athlete']['username']
        access_token = j['access_token']
        user_id = j['user_id']
        print(user_id)

        request.session['fitbit_access_token'] = access_token

        request.session['fitbit_user_id'] = user_id

        headers = {'Authorization':'Bearer ' + str(access_token)}

        rTwo = requests.get("https://api.fitbit.com/1/user/" + user_id + "/profile.json", data={}, headers=headers)

        jTwo = json.loads(rTwo.text)

        request.session['fitbit_name'] = jTwo['user']['displayName']

        return redirect('commuterform')


    else:
        return redirect('logout_all')


def fitbitupload(request, bikeTotal, runTotal, walkTotal, caloriesBurned):

    bikeTotal = int(bikeTotal)
    runTotal = int(runTotal)
    walkTotal = int(walkTotal)

    access_token = request.session['fitbit_access_token']

    user_id = request.session['fitbit_user_id']
    
    date = str(datetime.datetime.now().date())

    time = datetime.datetime.now().strftime("%H:%M:%S")

    params = {'activityName':'', 'manualCalories': str(caloriesBurned), 'startTime': time, 'durationMillis':'', 'date':date}

    headers = {'Authorization':'Bearer ' + str(access_token)}


    #bikeTotal = int(request.session['strava_bike_total'])

    if bikeTotal > 0:
        params['activityName'] = 'GSI Walk/Ride Day Commute (Bike)'
        params['durationMillis'] = bikeTotal * 60000

        r = requests.post("https://api.fitbit.com/1/user/" + str(user_id) + "/activities.json", data=params, headers=headers)

        print("yay")
        print(r.status_code)
        print(r.text)


    if runTotal > 0:
        params['activityName'] = 'GSI Walk/Ride Day Commute (Run)'
        params['durationMillis'] = runTotal * 60000

        r = requests.post("https://api.fitbit.com/1/user/" + str(user_id) + "/activities.json", data=params, headers=headers)

        print("yay run")
        print(r.status_code)
        print(r.text)


    if walkTotal > 0:
        params['activityName'] = 'GSI Walk/Ride Day Commute (Walk)'
        params['durationMillis'] = walkTotal * 60000

        r = requests.post("https://api.fitbit.com/1/user/" + str(user_id) + "/activities.json", data=params, headers=headers)

        print("yay walk")
        print(r.status_code)
        print(r.text)


    return HttpResponse('<h1>Page was found</h1>')
  













from __future__ import division
from django.shortcuts import render
from survey.models import Commutersurvey, Employer, Leg, Month, Team, Mode, Sector, get_surveys_by_employer, QuestionOfTheMonth, EmployerMonthInfo
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.db.models import Sum,Count
from django.db.models import Q
from aggregate_if import Count, Sum
from django.db.models import Count
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

from data import calculate_metrics, get_month_data, save_all_data

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import Legend

from datetime import date, datetime
from math import pi
import datetime
import random, string, os

#from django.core.mail import send_mail


def calculate_rankings(company_dict):
    ranks = {}
    ranks['percent_green_commuters'], ranks['percent_participation'], ranks['percent_green_switches'], ranks['percent_healthy_switches'], ranks['percent_avg_participation'] = [], [], [], [], []

    top_percent_green = sorted(company_dict.keys(), key=lambda x: company_dict[x]['already_green'], reverse=True)[:10]
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, company_dict[key]['already_green']])

    top_participation = sorted(company_dict.keys(), key=lambda x: company_dict[x]['participants'], reverse=True)[:10]
    for key in top_participation:
        ranks['percent_participation'].append([key, company_dict[key]['participants']])

    top_gs = sorted(company_dict.keys(), key=lambda x: company_dict[x]['green_switch'], reverse=True)[:10]
    for key in top_gs:
        ranks['percent_green_switches'].append([key, company_dict[key]['green_switch']])

    top_hs = sorted(company_dict.keys(), key=lambda x: company_dict[x]['healthy_switch'], reverse=True)[:10]
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, company_dict[key]['healthy_switch']])

    top_avg_participation = sorted(company_dict.keys(), key=lambda x: company_dict[x]['avg_participation'], reverse=True)[:10]
    for key in top_avg_participation:
        ranks['percent_avg_participation'].append([key, company_dict[key]['avg_participation']])

    return ranks


# If txt file with employer keys doesn't exist, call generate_keys() once
def generate_keys():
    for employer in Employer.objects.all():        
        if employer.secret_key_3 == "None":
            employer.secret_key_3 = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))
            employer.save()



def company(request, year=datetime.datetime.now().year, employerid=None, teamid=None):
#def company(request, year=2016, employerid=None, teamid=None):

    context = RequestContext(request)

    # use the year to set filtering

    activeFilter = "active{0}".format(year)

    if not employerid:
        companies = Employer.objects.exclude(id__in=[32,33,34,38,39,40]).filter(**{activeFilter: True})
        return render_to_response('pick_company.html', {
            'year': year,
            'companies': companies
            }, context)

    else:
        if teamid:
            company = Team.objects.get(id=teamid)
        else:
            company = Employer.objects.get(id=employerid)

        """
        Build dictionary storing results for all stats for all months
        """

        # Show detailed info about each firm: total check-ins, total CO2, Total Calories, monthly changes, new check-ins.
        allmetrics = calculate_metrics(company, 'all', year)
        overall = [
            ('Number of check-ins',
                allmetrics['num_checkins']),
            ('Estimated total CO2 (kg) saved by not driving on Walk/Ride Day',
                round(allmetrics['total_C02'],0)),
            ('Estimated total calories (kcal) burned during on Walk/Ride Day',  #Changed label from "on a Normal Day" to "on Walk/Ride Day"
                round(allmetrics['total_calories'],0)),
            ('Percent of team participating',
                '{0}%'.format(allmetrics['participants'])),
            ('Percent of check-ins involving a green commute on a normal day',
                '{0}%'.format(allmetrics['already_green'])),
            ('Number of people who made green switches',
                int(allmetrics['green_switch']*allmetrics['num_checkins']/100)),
            ('Number of people who made healthy switches',
                int(allmetrics['healthy_switch']*allmetrics['num_checkins']/100))
            ]

        if year == 2015:
            overall.extend([('Percent of check-ins where commutes went greener for Walk/Ride Day (April 2015)',
                    '{0}%'.format(calculate_metrics(company, 'april', '2015')['green_switch'])),
                ('Percent of check-ins where commutes went healthier for Walk/Ride Day (April 2015)',
                    '{0}%'.format(calculate_metrics(company, 'april', '2015')['healthy_switch']))])
        elif year >= 2016:
#       elif year == 2016:
            overall.extend([('Percent of check-ins where commutes went greener for Walk/Ride Day',
                    '{0}%'.format(allmetrics['green_switch'])),
                ('Percent of check-ins where commutes went healthier for Walk/Ride Day',
                    '{0}%'.format(allmetrics['healthy_switch']))])

        data = [
            # 0
            ('Impacts',
                'Everyone\'s check-in makes an impact on our world and ourselves! 430 kgs <a href="http://www.epa.gov/cleanenergy/energy-resources/refs.html">barrel of oil</a>',
                (
                    ('Estimated total CO2 (kg) saved by not driving on Walk/Ride Day', [], []),
                    ('Estimated total calories (kcal) burned during on Walk/Ride Day', [], [])    #Changed label from "on a Normal Day" to "on Walk/Ride Day"
                ) ),
            # 1
            ('Commutes',
                'Walk/Ride Day can change our commuting habits. Green commutes emit less carbon dioxide than typical car commutes, and can involve carpooling, walking, biking, running, and many forms of public transportation. Healthier commutes burn more calories, so break out the tennis shoes and get walking!',
                (
                    ('Percent of check-ins involving a green commute on a normal day', []),
                    ('Percent of check-ins where commutes went greener for Walk/Ride Day', []),
                    ('Percent of check-ins where commutes went healthier for Walk/Ride Day', [])
                ) ),
            # 2
            ('Participation',
                '',
                (
                    ('Number of check-ins', [], []),
                    ('Percent of team participating', [])
                ) )
        ]

        

        if int(datetime.datetime.now().year) > int(year):
            past_months = 7;
        else:
            # subtract 3 because jan/feb/mar are not in challenge
            past_months = past_months = datetime.datetime.now().month - 3


        months = ['april','may','june','july','august','september','october'][0:past_months]

        for month in reversed(months):
            metrics = calculate_metrics(company, month, year)
            data[0][2][0][1].append(
                (month, metrics['total_C02'])
                )
            data[0][2][1][1].append(
                (month, metrics['total_calories'])
                )
            data[1][2][0][1].append(
                (month, metrics['already_green'])
                )
            data[2][2][0][1].append(
                (month, metrics['num_checkins'])
                )
            data[2][2][1][1].append(
                (month, metrics['participants'])
                )
            if year == 2015:
                # april only!
                data[1][2][1][1].append(
                    ('april', calculate_metrics(company, 'april', '2015')['green_switch'])
                    )
                data[1][2][2][1].append(
                    ('april', calculate_metrics(company, 'april', '2015')['healthy_switch'])
                    )
            elif year >= 2016:
                data[1][2][1][1].append(
                    (month, metrics['green_switch'])
                    )
                data[1][2][2][1].append(
                    (month, metrics['healthy_switch'])
                    )

        # bonus numbers! if largest number exceeds 600, map to a different scale

        for blob in [data[0][2][0], data[0][2][1], data[2][2][1]]:
            values = [y for x,y in blob[1]]
            if max(abs(i) for i in values) > 600:
                m = max(abs(i) for i in values)
                adjusted = map(lambda x: (x/m * 600), values)
                months = [x for x,y in blob[1]]
                for i in xrange(len(months)):
                    blob[2].append((months[i],adjusted[i],values[i]))

        now = datetime.datetime.now()
        if year != now.year:
            int_month = 11
        if now.month in [1,2,3,12]:
            int_month = 11
        else:
            int_month = now.month

        int_month -= 1
        int_to_intstr_month = {4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09", 10: "10"}
        month = int_to_intstr_month[int_month]

        int_to_month_string = {'04': "April", '05': "May", '06': "June", '07': "July", '08': "August", '09': "September", '10': "October", 'all': 'All'}
        current_month = int_to_month_string[month]

        all_months_modes = {}

        long_months = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'All']
        short_months = ['04','05','06','07','08','09','10', 'all']

        for month in long_months:
            all_months_modes[month] = {}

        for month in short_months:
            surveys = get_surveys_by_employer(company, month, year) 
            employer_legs_n = {}  # totals for each mode
            employer_legs_wr = {}
            for survey in surveys:
                
                legs_n, legs_wr = survey.get_legs()

                info = {}

                info['legs_n'], info['legs_wr'] = legs_n, legs_wr

                for legs, employer_legs in [(legs_n, employer_legs_n), (legs_wr, employer_legs_wr)]:
                    person_modes = set()
                    for leg in legs:
                        if leg['mode'] not in employer_legs:
                            employer_legs[leg['mode']] = {'duration': leg['duration'], 'calories': leg['calories'], 'carbon': leg['carbon'], 'people': 1}
                            person_modes.add(leg['mode'])
                        elif leg['mode'] in employer_legs:
                            employer_legs[leg['mode']]['duration'] += leg['duration']
                            employer_legs[leg['mode']]['calories'] += leg['calories']
                            employer_legs[leg['mode']]['carbon'] += leg['carbon']
                            if leg['mode'] not in person_modes:
                                employer_legs[leg['mode']]['people'] += 1
                                person_modes.add(leg['mode'])
                    person_modes = set()

            all_months_modes[int_to_month_string[month]]['legs_n'] = employer_legs_n
            all_months_modes[int_to_month_string[month]]['legs_wr'] = employer_legs_wr
            

        return render_to_response('company.html',
        {       'year': year,
                'company': company,
                'impacts': data[0],
                'commutes': data[1],
                'participation': data[2],
                'overall': overall,
                'all_months_modes': all_months_modes,
                'current_month': current_month,
                'months': long_months,
            }, context)

def latest_leaderboard(request, year=datetime.datetime.now().year, sector='all', size='all', parentid=None, selected_month='all'):


    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    if year is None:
        return redirect('2017/')

    d = {}

    parent = None

    # use the year to set filtering on Employer, Commutersurvey, etc.
    activeFilter = "active{0}".format(year)

    if parentid: # this is a bunch of subteams
        parent = Employer.objects.filter(**{activeFilter: True}).get(id=parentid)

        teams = Team.objects.only('id','name').filter(parent_id=parentid)

        survey_data = teams

    else: # this is a bunch of companies
        companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34,38,39,40]).filter(**{activeFilter: True})

        # Filtering the results by size
        if size == 'small':
            companies = companies.filter(nr_employees__lte=50)
        elif size == 'medium':
            companies = companies.filter(nr_employees__gt=50,nr_employees__lte=300)
        elif size == 'large':
            companies = companies.filter(nr_employees__gt=300,nr_employees__lte=2000)
        elif size == 'largest':
            companies = companies.filter(nr_employees__gt=2000)

        # Filtering the results by sector
        if sector != 'all':
            selected_sector = Sector.objects.get(short=sector).name
            companies = companies.filter(sector__short=sector)
        else:
            selected_sector = ''
            selected_sector_name = 'All Sectors'

        survey_data = companies

    if selected_month != 'all':
        months_dict = { 'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12' }
        shortmonth = months_dict[selected_month]
        month_model = Month.objects.filter(wr_day__year=year, wr_day__month=shortmonth)
        survey_data = survey_data.filter(commutersurvey__wr_day_month=month_model)
    else:
        month_models = Month.objects.filter(wr_day__year=year).exclude(wr_day__month='01').exclude(wr_day__month='02').exclude(wr_day__month='03').exclude(wr_day__month='11').exclude(wr_day__month='12')
        survey_data = survey_data.filter(commutersurvey__wr_day_month=month_models)

    survey_data = survey_data.annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = survey_data.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in survey_data:
        # links is company id, then optionally team id
        if hasattr(company, 'parent'): # then this is a team
            links = (company.parent.id, company.id)
        else:
            links = (company.id,)
        d[(str(company.name), links)] = calculate_metrics(company, selected_month, year)

    ranks = calculate_rankings(d)

    sectors_dict = dict(Sector.objects.values_list('short','name'))
    months_arr = ['april', 'may', 'june', 'july', 'august', 'september', 'october']
    sizes_arr = [
      ('small', 'Small (fewer than 50)'),
      ('medium', 'Medium (51 to 300)'),
      ('large', 'Large (301 to 2000)'),
      ('largest', 'Largest (2001+ employees)')
    ]

    return render_to_response('leaderboard/leaderboard_new.html',
    {
        'year': year,
        'ranks': ranks,
        'totals': totals,
        'request': request,
        'employersWithSubteams': Employer.objects.filter(**{activeFilter: True}).filter(team__isnull=False).distinct(),
        'size': size,
        'selected_month': selected_month,
        'parent': parent,
        'selected_sector': sector,
        'sizes_list': sizes_arr,
        'months_list': months_arr,
        'sectors_list': sectors_dict
    }, context)


def cumulative(year, employer):  # calculate statistics for employer for the year
    carbon_n = employer.total_C02_n('all',year)
    carbon_wr = employer.total_C02_wr('all', year)
    carbon_saved = employer.total_C02('all', year)
    all_legs_n = {}
    all_legs_wr = {}
    employer_info = calculate_metrics(employer, 'all', 2016)
    calories_wr = employer.total_calories('all', year)
    calories_n = employer.total_calories_n('all', year)
    num_checkins = employer.count_checkins('all', year)

    short_months = ['04','05','06','07','08','09','10']
    for month in short_months:
        month_data = get_month_data(employer, month, year)
        if not month_data:
            continue
        for mode, leg in month_data['employer_legs_wr'].items():
            if mode not in all_legs_wr:
                all_legs_wr[mode] = leg
            elif mode in all_legs_wr:
                all_legs_wr[mode]['duration'] += leg['duration']
                all_legs_wr[mode]['calories'] += leg['calories']
                all_legs_wr[mode]['carbon'] += leg['carbon']
                all_legs_wr[mode]['people'] += leg['people']
        for mode, leg in month_data['employer_legs_n'].items():
            if mode not in all_legs_n:
                all_legs_n[mode] = leg
            elif mode in all_legs_n:
                all_legs_n[mode]['duration'] += leg['duration']
                all_legs_n[mode]['calories'] += leg['calories']
                all_legs_n[mode]['carbon'] += leg['carbon']
                all_legs_n[mode]['people'] += leg['people']

    return {'num_checkins': num_checkins, 'calories_n': calories_n, 'calories_wr': calories_wr, 'carbon_n': carbon_n, 'carbon_wr': carbon_wr,
            'carbon_saved': carbon_saved, 'all_legs_n': all_legs_n, 'all_legs_wr': all_legs_wr}

def get_month_years(shortmonth, year):  # Gets past 7 months
    months = ['04', '05', '06', '07', '08', '09', '10']
    month_index = None
    for i, x in enumerate(months):
        if x == shortmonth:
            month_index = i
            break
    if shortmonth in ['01', '02', '03', '11', '12']:
        month_index = len(months) - 1  # october if month is nov, jan, feb, mar
        if shortmonth in ['01', '02', '03']:                
            year -= 1
    # Are jan feb mar in wrd?
    months_to_str = {'04': 'Apr', '05': 'May', '06': 'Jun',  '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct'}
    month_years = []
    month_years_tuples = []
    for i in xrange(0, month_index+1):
        month_years_tuples.append((months[i], year))
        month_years.append(months_to_str[months[i]] + ' ' + str(year))
    return month_years_tuples, month_years  # month_years_tuples is a list of (shortmonth, year) and month_years is a list of "Jan 2016"
        
def carbon_employer_graph(employer, shortmonth, year):  # Display for past 7 months
    month_years_tuples, month_years = get_month_years(shortmonth, year)
    legend_labels = ["Walk Ride Day", "Normal Day", "CO2 Emitted While Driving Alone"]
    carbon_wr = []
    carbon_n = []
    carbon_driving = []
    for month, year in month_years_tuples:
        carbon_wr.append(employer.total_C02_wr(month, year))
        carbon_n.append(employer.total_C02_n(month, year))
        carbon_driving.append(employer.total_C02(month, year) + employer.total_C02_wr(month, year))
    return line_graph(month_years, [carbon_wr, carbon_n, carbon_driving], legend_labels, "Month", "Carbon Dioxide Emissions (kg)", "Your Company's Carbon Dioxide Emissions")

def calories_employer_graph(employer, shortmonth, year):
    month_years_tuples, month_years = get_month_years(shortmonth, year)
    legend_labels = ["Walk Ride Day", "Normal Day"]
    calories_wr = []
    calories_n = []
    for month, year in month_years_tuples:
        calories_wr.append(employer.total_calories(month, year))
        calories_n.append(employer.total_calories_n(month, year))
    return line_graph(month_years, [calories_wr, calories_n], legend_labels, "Month", "Calories Burned (kcal)", "Your Company's Calories")

def make_change_line_graph(company, current_month, current_year):
    already_green_y = []
    green_switch_y = []
    healthy_switch_y = []

    int_to_str = {4: "april", 5: "may", 6: "june", 7: "july", 8: "august", 9: "september", 10: "october"}
    months = ["april", "may", "june", "july", "august", "september", "october"]
    int_to_intstr_month = {"april": "04", "may": "05", "june": "06", "july": "07", "august": "08", "september": "09", "october": "10"}

    year = current_year
    if current_month in [11, 12, 1, 2, 3]:
        current_month = 10
        if current_month in [1, 2, 3]:
            year = current_year - 1
    current_month = int_to_str[current_month]
    showing = [(current_month, year)]
    current_month_index = months.index(current_month)

    for n in range(current_month_index):
        i = months.index(current_month)
        i -= 1
        current_month = months[i]
        showing.insert(0, (current_month, current_year))

    for month_year in showing:
        month, year = month_year
        shortmonth = int_to_intstr_month[month]
        already_green_y.append(company.num_already_green(shortmonth, year))
        green_switch_y.append(company.num_green_switch(shortmonth, year))
        healthy_switch_y.append(company.num_healthy_switch(shortmonth, year))

    abb = {"april": "Apr", "may": "May", "june": "Jun", "july": "Jul", "august": "Aug", "september": "Sept", "october": "Oct"}
    
    x = []
    for month_year in showing:
        month, year = month_year
        x.append(abb[month] + " " + str(year))

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    g = figure(title="Your Company's Commute Changes", tools=TOOLS, x_range = x, toolbar_location="above")

    r0 = g.circle(x, already_green_y, line_color="green", fill_color="green")
    r1 = g.line(x, already_green_y, line_color="green", line_width=2)

    r2 = g.circle(x, green_switch_y, line_color="blue", fill_color="blue")
    r3 = g.line(x, green_switch_y, line_color="blue", line_width=2)

    r4 = g.circle(x, healthy_switch_y, line_color="orange", fill_color="orange")
    r5 = g.line(x, healthy_switch_y, line_color="orange", line_width=2)

    legend = Legend(items=[
        ("already green", [r0, r1]),
        ("green switch", [r2, r3]),
        ("healthy switch", [r4, r5]),
    ], location=(30, 0))

    g.add_layout(legend, 'above')
    g.xaxis.major_label_orientation = pi/4
    g.yaxis.axis_label = "Number of People"
    
    script, div = components(g)
    return script, div

def line_graph(x, y, legend_labels, x_label, y_label, title):

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"  #hover?

    y_max = max(max(_ for _ in y))

    p = figure(title=title, tools=TOOLS, x_range=x, y_range=[-2,y_max+5])

    colors = ["green", "orange", "blue"]
    legend_items = []

    for i in xrange(len(legend_labels)):
        c = p.circle(x, y[i], color=colors[i])
        l = p.line(x, y[i], line_color=colors[i], line_width=2)
        legend_items.append((legend_labels[i], [c, l]))

    legend = Legend(items=legend_items, location=(30, 0))

    p.add_layout(legend, 'above')
    p.xaxis.major_label_orientation = pi/4
    p.yaxis.axis_label = y_label
    #output_file("graph.html", title="Example")
    script, div = components(p)
    return script, div
    
#Employer Information Page
def info(request, secret_code, year):    
    employer_id = None
    generate_keys()

    for employer in Employer.objects.all():
        
        year_secret_key = secret_code + "-" + str(year)

        if secret_code == employer.secret_key_3 or year_secret_key == employer.secret_key_3:
            employer_id = employer.id
    
    if employer_id is None:
        return HttpResponse('<html><head></head><body><b>Error</b><br/>The company keys have changed. We apologize for any inconvenience.</br>Please contact the GSI Director Janie at <span style="color:#339933"><b>jkatzchristy@gogreenstreets.org</b></span> to receive your new key.</body></html>')

    now = datetime.datetime.now()
    if year != now.year:
        int_month = 11
    if now.month in [1,2,3,12]:
        int_month = 11
    else:
        int_month = now.month
    # int_month -= 1
    int_to_intstr_month = {4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09", 10: "10"}
    month = int_to_intstr_month[int_month]

    int_to_month_string = {'04': "April", '05': "May", '06': "June", '07': "July", '08': "August", '09': "September", '10': "October"}
    current_month = int_to_month_string[month]

    employer = Employer.objects.get(id=employer_id)

    all_months_data = {}
    long_months = ['April', 'May', 'June', 'July', 'August', 'September', 'October']
    short_months = ['04','05','06','07','08','09','10']
    employees_totals = {}
    count = 0
    for month in short_months:
        month_data = get_month_data(employer, month, year)
        all_months_data[int_to_month_string[month]] = month_data
        if not month_data:
            continue
        count += month_data["employer_info"]["count"]
        for letter, employees in month_data['employees_by_letter'].items():
            if letter != 'all':
                for info in employees: 
                    email = info['email']
                    if email in employees_totals: # modes > duration, calories, co2 emitted
                        employees_totals[email]["carbon_change"] += info["carbon_change"]
                        employees_totals[email]["calorie_change"] += info["calorie_change"]
                        employees_totals[email]["num_checkins"] += 1
                    else:
                        employees_totals[email] = {'home_address': info['home_address'], 'letter': letter, 'num_checkins': 1, 'first': info['first'], 'last': info['last'], 'email': email, "carbon_change": info["carbon_change"], "calorie_change": info["calorie_change"], 'legs_n': [], 'legs_wr': []}

                    for legs, legs_total in [(info['legs_n'], employees_totals[email]['legs_n']), (info['legs_wr'], employees_totals[email]['legs_wr'])]:
                        for leg in legs:
                            added = False
                            for leg_total in legs_total:
                                if str(leg['mode']) == str(leg_total['mode']):
                                    leg_total['duration'] += leg['duration']
                                    leg_total['calories'] += leg['calories']
                                    leg_total['carbon'] += leg['carbon']
                                    added = True
                                    break
                            if not added:
                                legs_total.append(leg)

    employees_totals_by_letter = {}
    letters = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    for letter in letters: 
        employees_totals_by_letter[letter] = []
    #Sort alphabetically by last name
    info_id = 0
    for info in employees_totals.values():
        info['id'] = info_id
        info_id += 1
        if info['carbon_change'] < -0.5 or info['calorie_change'] > 0.5:
            color = "green"
        else:
            color = "black"
        info['color'] = color
        people = employees_totals_by_letter[info['letter']]  # list of people already in totals_by_letter list starting with first letter of lastname
        people.append(info)
        people.sort(key=lambda x: x['last'])
    employees_totals_by_letter['all'] = []     
    for letter, employees in employees_totals_by_letter.items():
        if letter != 'all':
            employees_totals_by_letter['all'].extend(employees)
    employees_totals_by_letter['all'].sort(key=lambda x: x['last'])

    carbon_employer_script, carbon_employer_div = carbon_employer_graph(employer, month, year)
    calories_employer_script, calories_employer_div = calories_employer_graph(employer, month, year)
    change_script, change_div = make_change_line_graph(employer, int(month), year)
    cumulative_data = cumulative(year, employer)

    return render_to_response('employer.html', {
        'all_months_data': all_months_data,
        'employer': employer,
        'letters': letters,
        'cumulative': cumulative_data,
        'carbon_employer_script': carbon_employer_script,
        'carbon_employer_div': carbon_employer_div,
        'calories_employer_script': calories_employer_script,
        'calories_employer_div': calories_employer_div,
        'change_script': change_script,
        'change_div': change_div,
        'current_month': current_month,
        'year': year,
        'months': long_months,
        'employees_totals_by_letter': employees_totals_by_letter,
        'all_count': count,
    })

# Render data for all months for Employer Information Page
@user_passes_test(lambda u: u.is_superuser)
def render(request, employerid, shouldreplace):
    replace = False
    if shouldreplace == 'replace':
        replace = True
    if employerid != 'all':
        try:
            employer = Employer.objects.get(id=employerid)
            save_all_data(employer, replace)
            return HttpResponse('Data rendered for ' + employer.name)
        except Employer.DoesNotExist:
            return HttpResponse('Invalid employer ID')
    elif employerid == 'all':
        save_all_data(replace=replace)
        return HttpResponse('Data rendered for all employers.')
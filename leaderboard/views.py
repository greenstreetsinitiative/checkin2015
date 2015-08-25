from __future__ import division
from django.shortcuts import render
from survey.models import Commutersurvey, Employer, Leg, Month, Team, Mode
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.db.models import Sum,Count
from django.db.models import Q
from aggregate_if import Count, Sum
from django.db.models import Count

from datetime import date, datetime
import datetime

def calculate_rankings(company_dict):
    ranks = {}
    ranks['percent_green_commuters'], ranks['percent_participation'], ranks['percent_green_switches'], ranks['percent_healthy_switches'], ranks['percent_avg_participation'] = [],[],[],[],[]

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


def calculate_metrics(company, selected_month):

    months_dict = { 'all': 'all', 'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12' }
    shortmonth = months_dict[selected_month]

    percent_participants = 100*company.percent_participation(shortmonth)
    percent_already_green = 100*company.percent_already_green(shortmonth)
    percent_green_switch = 100*company.percent_green_switch(shortmonth)
    percent_healthy_switch = 100*company.percent_healthy_switch(shortmonth)
    percent_participants_average = 100*company.average_percent_participation()
    count_checkins = company.count_checkins(shortmonth)
    total_C02 = company.total_C02(shortmonth)
    total_calories = company.total_calories(shortmonth)

    return {
        'participants': round(percent_participants,2),
        'already_green': round(percent_already_green,2),
        'green_switch': round(percent_green_switch,2),
        'healthy_switch': round(percent_healthy_switch,2),
        'avg_participation': round(percent_participants_average,2),
        'num_checkins': count_checkins,
        'total_C02': total_C02,
        'total_calories': total_calories
        }

def company(request, employerid=None, teamid=None):
    context = RequestContext(request)

    if not employerid:
        companies = Employer.objects.exclude(id__in=[32,33,34,38,39,40]).filter(active2015=True)
        return render_to_response('pick_company.html', { 'companies': companies }, context)

    else:
        if teamid:
            company = Team.objects.get(id=teamid)
        else:
            company = Employer.objects.get(id=employerid)

        """
        Build dictionary storing results for all stats for all months
        """

        # Show detailed info about each firm: total check-ins, total CO2, Total Calories, monthly changes, new check-ins.
        allmetrics = calculate_metrics(company, 'all')
        overall = [
            ('Number of check-ins',
                allmetrics['num_checkins']),
            ('Estimated total CO2 saved by not driving on Walk/Ride Day',
                round(allmetrics['total_C02'],0)),
            ('Estimated total calories burned on Walk/Ride Day',
                round(allmetrics['total_calories'],0)),
            ('Percent of team participating',
                '{0}%'.format(allmetrics['participants'])),
            ('Percent of check-ins involving a green commute on a normal day',
                '{0}%'.format(allmetrics['already_green'])),
            ('Percent of check-ins where commutes went greener for Walk/Ride Day',
                '{0}%'.format(allmetrics['green_switch'])),
            ('Percent of check-ins where commutes went healthier for Walk/Ride Day',
                '{0}%'.format(allmetrics['healthy_switch']))
            ]

        data = [
            ('Impacts',
                'Everyone\'s check-in makes an impact on our world and ourselves! 430 kgs <a href="http://www.epa.gov/cleanenergy/energy-resources/refs.html">barrel of oil</a>',
                (
                    ('Estimated total kg CO2 saved by not driving on Walk/Ride Day', [], []),
                    ('Estimated total calories burned on Walk/Ride Day', [], [])
                ) ),
            ('Commutes',
                'Walk/Ride Day can change our commuting habits. Green commutes emit less carbon dioxide than typical car commutes, and can involve carpooling, walking, biking, running, and many forms of public transportation. Healthier commutes burn more calories, so break out the tennis shoes and get walking!',
                (
                    ('Percent of check-ins involving a green commute on a normal day', []),
                    ('Percent of check-ins where commutes went greener for Walk/Ride Day', []),
                    ('Percent of check-ins where commutes went healthier for Walk/Ride Day', [])
                ) ),
            ('Participation',
                '',
                (
                    ('Number of check-ins', [], []),
                    ('Percent of team participating', [])
                ) )
        ]

        past_months = Month.objects.filter(open_checkin__lte=date.today(), open_checkin__gt=('2015-03-31')).count()
        months = ['april','may','june','july','august','september','october'][0:past_months]

        for month in reversed(months):
            metrics = calculate_metrics(company, month)
            data[0][2][0][1].append(
                (month, metrics['total_C02'])
                )
            data[0][2][1][1].append(
                (month, metrics['total_calories'])
                )
            data[1][2][0][1].append(
                (month, metrics['already_green'])
                )
            data[1][2][1][1].append(
                (month, metrics['green_switch'])
                )
            data[1][2][2][1].append(
                (month, metrics['healthy_switch'])
                )
            data[2][2][0][1].append(
                (month, metrics['num_checkins'])
                )
            data[2][2][1][1].append(
                (month, metrics['participants'])
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

        return render_to_response('company.html',
            {   'company': company,
                'impacts': data[0],
                'commutes': data[1],
                'participation': data[2],
                'overall': overall
            }, context)

def latest_leaderboard(request, size='all', parentid=None, selected_month='all'):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    parent = None

    if parentid: # this is a bunch of subteams
        parent = Employer.objects.get(id=parentid)

        teams = Team.objects.only('id','name').filter(parent_id=parentid)

        survey_data = teams

    else: # this is a bunch of companies
        companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34,38,39,40]).filter(active2015=True)

        # Filtering the results by size
        if size == 'small':
            companies = companies.filter(nr_employees__lte=50)
        elif size == 'medium':
            companies = companies.filter(nr_employees__gt=50,nr_employees__lte=300)
        elif size == 'large':
            companies = companies.filter(nr_employees__gt=300,nr_employees__lte=2000)
        elif size == 'largest':
            companies = companies.filter(nr_employees__gt=2000)

        survey_data = companies

    if selected_month != 'all':
        months_dict = { 'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12' }
        shortmonth = months_dict[selected_month]
        month_model = Month.objects.filter(wr_day__year='2015', wr_day__month=shortmonth)
        survey_data = survey_data.filter(commutersurvey__wr_day_month=month_model)

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
        d[str(company.name)] = calculate_metrics(company, selected_month)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html',
        {
            'ranks': ranks,
            'totals': totals,
            'request': request,
            'employersWithSubteams': Employer.objects.filter(team__isnull=False).distinct(),
            'size': size,
            'selected_month': selected_month,
            'parent': parent
        }, context)

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


def calculate_metrics(company):

    employee_engagement = {}

    if company.nr_employees > 0:
        employee_engagement["perc_participants"] = company.num_participants*100 / company.nr_employees
    else:
        employee_engagement["perc_participants"] = 0

    if employee_engagement["perc_participants"] > 100:
        employee_engagement["perc_participants"] = 100

    # TODO: How does this update as the challenge goes? Use all challenges that have happened so far instead of 7
    # TODO count participants even if without an email or name OR make name and email required fields
    # if company.num_participants > 0:
    #     employee_engagement["avg_frequency"] = employee_engagement["checkins"]*100 / (employee_engagement["num_participants"] * 7)
    # else: 
    #     employee_engagement["avg_frequency"] = 0

    green_momentum = {}

    if company.num_checkins > 0:
        green_momentum["perc_already_green"] = company.num_already_green*100 / company.num_checkins
    else:
        green_momentum["perc_already_green"] = 0

    if green_momentum["perc_already_green"] > 100:
        green_momentum["perc_already_green"] = 100

    behavior_change = {}

    if company.num_checkins > 0:
        behavior_change["perc_green"] = company.num_switch_green*100 / company.num_checkins

        behavior_change["perc_healthy"] = company.num_switch_healthy*100 / company.num_checkins

    else:
        behavior_change["perc_green"] = 0
        behavior_change["perc_healthy"] = 0

    if behavior_change["perc_green"] > 100:
        behavior_change["perc_green"] = 100

    if behavior_change["perc_healthy"] > 100:
        behavior_change["perc_healthy"] = 100

    return {'engagement': employee_engagement, 'green': green_momentum, 'behavior': behavior_change }


def latest_leaderboard(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').filter(
        active2015=True, 
        commutersurvey__created__gte=datetime.date(2015, 04, 15), 
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        overall_carbon=Sum('commutersurvey__carbon_change'),
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calorie_change'),
        num_checkins=(Count('commutersurvey')),
        num_participants=Count('commutersurvey__email', distinct=True),
        num_already_green=Count('commutersurvey', only=Q(commutersurvey__already_green=True)),
        num_switch_green=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['g','p'])),
        num_switch_healthy=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['h','p']))
    )

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = {}

    top_percent_green = sorted(d.keys(), key=lambda x: d[x]['green']['perc_already_green'], reverse=True)[:10]
    ranks['percent_green_commuters'] = []
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, d[key]['green']['perc_already_green']])

    top_participation = sorted(d.keys(), key=lambda x: d[x]['engagement']['perc_participants'], reverse=True)[:10]
    ranks['percent_participation'] = []
    for key in top_participation:
        ranks['percent_participation'].append([key, d[key]['engagement']['perc_participants']])

    top_gs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_green'], reverse=True)[:10]
    ranks['percent_green_switches'] = []
    for key in top_gs:
        ranks['percent_green_switches'].append([key, d[key]['behavior']['perc_green']])

    top_hs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_healthy'], reverse=True)[:10]
    ranks['percent_healthy_switches'] = []
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, d[key]['behavior']['perc_healthy']])

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals }, context)

def latest_leaderboard_small(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').filter(
        nr_employees__lte=50,
        active2015=True, 
        commutersurvey__created__gte=datetime.date(2015, 04, 15), 
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        overall_carbon=Sum('commutersurvey__carbon_change'),
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calorie_change'),
        num_checkins=Count('commutersurvey'),
        num_participants=Count('commutersurvey__email', distinct=True),
        num_already_green=Count('commutersurvey', only=Q(commutersurvey__already_green=True)),
        num_switch_green=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['g','p'])),
        num_switch_healthy=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['h','p']))
    )

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = {}

    top_percent_green = sorted(d.keys(), key=lambda x: d[x]['green']['perc_already_green'], reverse=True)[:10]
    ranks['percent_green_commuters'] = []
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, d[key]['green']['perc_already_green']])

    top_participation = sorted(d.keys(), key=lambda x: d[x]['engagement']['perc_participants'], reverse=True)[:10]
    ranks['percent_participation'] = []
    for key in top_participation:
        ranks['percent_participation'].append([key, d[key]['engagement']['perc_participants']])

    top_gs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_green'], reverse=True)[:10]
    ranks['percent_green_switches'] = []
    for key in top_gs:
        ranks['percent_green_switches'].append([key, d[key]['behavior']['perc_green']])

    top_hs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_healthy'], reverse=True)[:10]
    ranks['percent_healthy_switches'] = []
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, d[key]['behavior']['perc_healthy']])

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals }, context)


def latest_leaderboard_medium(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').filter(
        nr_employees__gt=50,
        nr_employees__lte=300,
        active2015=True, 
        commutersurvey__created__gte=datetime.date(2015, 04, 15), 
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        overall_carbon=Sum('commutersurvey__carbon_change'),
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calorie_change'),
        num_checkins=Count('commutersurvey'),
        num_participants=Count('commutersurvey__email', distinct=True),
        num_already_green=Count('commutersurvey', only=Q(commutersurvey__already_green=True)),
        num_switch_green=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['g','p'])),
        num_switch_healthy=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['h','p']))
    )

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = {}

    top_percent_green = sorted(d.keys(), key=lambda x: d[x]['green']['perc_already_green'], reverse=True)[:10]
    ranks['percent_green_commuters'] = []
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, d[key]['green']['perc_already_green']])

    top_participation = sorted(d.keys(), key=lambda x: d[x]['engagement']['perc_participants'], reverse=True)[:10]
    ranks['percent_participation'] = []
    for key in top_participation:
        ranks['percent_participation'].append([key, d[key]['engagement']['perc_participants']])

    top_gs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_green'], reverse=True)[:10]
    ranks['percent_green_switches'] = []
    for key in top_gs:
        ranks['percent_green_switches'].append([key, d[key]['behavior']['perc_green']])

    top_hs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_healthy'], reverse=True)[:10]
    ranks['percent_healthy_switches'] = []
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, d[key]['behavior']['perc_healthy']])

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals }, context)

def latest_leaderboard_large(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').filter(
        nr_employees__gt=300,
        nr_employees__lte=2000,
        active2015=True, 
        commutersurvey__created__gte=datetime.date(2015, 04, 15), 
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        overall_carbon=Sum('commutersurvey__carbon_change'),
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calorie_change'),
        num_checkins=Count('commutersurvey'),
        num_participants=Count('commutersurvey__email', distinct=True),
        num_already_green=Count('commutersurvey', only=Q(commutersurvey__already_green=True)),
        num_switch_green=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['g','p'])),
        num_switch_healthy=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['h','p']))
    )

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = {}

    top_percent_green = sorted(d.keys(), key=lambda x: d[x]['green']['perc_already_green'], reverse=True)[:10]
    ranks['percent_green_commuters'] = []
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, d[key]['green']['perc_already_green']])

    top_participation = sorted(d.keys(), key=lambda x: d[x]['engagement']['perc_participants'], reverse=True)[:10]
    ranks['percent_participation'] = []
    for key in top_participation:
        ranks['percent_participation'].append([key, d[key]['engagement']['perc_participants']])

    top_gs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_green'], reverse=True)[:10]
    ranks['percent_green_switches'] = []
    for key in top_gs:
        ranks['percent_green_switches'].append([key, d[key]['behavior']['perc_green']])

    top_hs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_healthy'], reverse=True)[:10]
    ranks['percent_healthy_switches'] = []
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, d[key]['behavior']['perc_healthy']])

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals }, context)

def latest_leaderboard_largest(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').filter(
        nr_employees__gt=2000,
        active2015=True, 
        commutersurvey__created__gte=datetime.date(2015, 04, 15), 
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        overall_carbon=Sum('commutersurvey__carbon_change'),
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calorie_change'),
        num_checkins=Count('commutersurvey'),
        num_participants=Count('commutersurvey__email', distinct=True),
        num_already_green=Count('commutersurvey', only=Q(commutersurvey__already_green=True)),
        num_switch_green=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['g','p'])),
        num_switch_healthy=Count('commutersurvey', only=Q(commutersurvey__change_type__in=['h','p']))
    )

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = {}

    top_percent_green = sorted(d.keys(), key=lambda x: d[x]['green']['perc_already_green'], reverse=True)[:10]
    ranks['percent_green_commuters'] = []
    for key in top_percent_green:
        ranks['percent_green_commuters'].append([key, d[key]['green']['perc_already_green']])

    top_participation = sorted(d.keys(), key=lambda x: d[x]['engagement']['perc_participants'], reverse=True)[:10]
    ranks['percent_participation'] = []
    for key in top_participation:
        ranks['percent_participation'].append([key, d[key]['engagement']['perc_participants']])

    top_gs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_green'], reverse=True)[:10]
    ranks['percent_green_switches'] = []
    for key in top_gs:
        ranks['percent_green_switches'].append([key, d[key]['behavior']['perc_green']])

    top_hs = sorted(d.keys(), key=lambda x: d[x]['behavior']['perc_healthy'], reverse=True)[:10]
    ranks['percent_healthy_switches'] = []
    for key in top_hs:
        ranks['percent_healthy_switches'].append([key, d[key]['behavior']['perc_healthy']])

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals }, context)



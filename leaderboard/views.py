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
    ranks['percent_green_commuters'], ranks['percent_participation'], ranks['percent_green_switches'], ranks['percent_healthy_switches'] = [],[],[],[]

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

    return ranks


def calculate_metrics(company):
    percent_participants = 100*company.percent_participation()
    percent_already_green = 100*company.percent_already_green()
    percent_green_switch = 100*company.percent_green_switch()
    percent_healthy_switch = 100*company.percent_healthy_switch()

    return {
        'participants': percent_participants,
        'already_green': percent_already_green,
        'green_switch': percent_green_switch,
        'healthy_switch': percent_healthy_switch
        }

def latest_leaderboard_subteams(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    teams = Team.objects.only('id','name').filter(commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = teams.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for team in teams:
        d[str(team.parent.name + ' - ' + team.name)] = calculate_metrics(team)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request }, context)

def latest_leaderboard(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34]).filter(
        active2015=True,
        commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request }, context)

def latest_leaderboard_small(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34]).filter(
        nr_employees__lte=50,
        active2015=True,
        commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request}, context)


def latest_leaderboard_medium(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34]).filter(
        nr_employees__gt=50,
        nr_employees__lte=300,
        active2015=True,
        commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request }, context)

def latest_leaderboard_large(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34]).filter(
        nr_employees__gt=300,
        nr_employees__lte=2000,
        active2015=True,
        commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request }, context)

def latest_leaderboard_largest(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    d = {}

    ### TODO - filter related commutersurveys by MONTH

    companies = Employer.objects.only('id','name').exclude(id__in=[32,33,34]).filter(
        nr_employees__gt=2000,
        active2015=True,
        commutersurvey__created__gte=datetime.date(2015, 04, 15),
        commutersurvey__created__lte=datetime.date(2015, 11, 01)).annotate(
        saved_carbon=Sum('commutersurvey__carbon_savings'),
        overall_calories=Sum('commutersurvey__calories_total'),
        num_checkins=Count('commutersurvey'))

    totals = companies.aggregate(
        total_carbon=Sum('saved_carbon'),
        total_calories=Sum('overall_calories'),
        total_checkins=Sum('num_checkins')
    )

    for company in companies:
        d[str(company.name)] = calculate_metrics(company)

    ranks = calculate_rankings(d)

    return render_to_response('leaderboard/leaderboard_new.html', { 'ranks': ranks, 'totals': totals, 'request': request }, context)

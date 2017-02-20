from survey.models import Commutersurvey, Employer, Leg, Month, Team, Mode, Sector, get_surveys_by_employer, QuestionOfTheMonth, EmployerMonthInfo

from datetime import date, datetime
from math import pi
import datetime
import json
import random, string, os


def calculate_metrics(company, selected_month, year):

    months_dict = { 'all': 'all', 'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12' }
    shortmonth = months_dict[selected_month]

    percent_participants = 100*company.percent_participation(shortmonth, year)
    percent_already_green = 100*company.percent_already_green(shortmonth, year)
    percent_green_switch = 100*company.percent_green_switch(shortmonth, year)
    percent_healthy_switch = 100*company.percent_healthy_switch(shortmonth, year)
    percent_participants_average = 100*company.average_percent_participation(year)
    count_checkins = company.count_checkins(shortmonth, year)
    total_C02 = company.total_C02(shortmonth, year)
    total_calories = company.total_calories(shortmonth, year)

    return {
        'participants': min(round(percent_participants,2), 100),
        'already_green': min(round(percent_already_green,2), 100),
        'green_switch': min(round(percent_green_switch,2), 100),
        'healthy_switch': min(round(percent_healthy_switch,2), 100),
        'avg_participation': min(round(percent_participants_average,2), 100),
        'num_checkins': count_checkins,
        'total_C02': total_C02,
        'total_calories': total_calories
        }

def render_month_data(employer, month, year):
    int_to_month_string = {'04': "April", '05': "May", '06': "June", '07': "July", '08': "August", '09': "September", '10': "October"}
    wr_month = int_to_month_string[month] + ' ' + str(year)
    months = Month.objects.all()
    month_class = None
    for m in months:
        if m.month == wr_month:
            month_class = m
            break
    if QuestionOfTheMonth.objects.filter(wr_day_month=month_class).count() == 0:
        question = ''
    else:
        question = QuestionOfTheMonth.objects.get(wr_day_month=month_class).value  

    surveys = get_surveys_by_employer(employer, month, year)  #8, 2016

    letters = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']  # For displaying ABCDE... tabs
    comments = []
    employees_by_letter = {}
    for letter in letters:  # Group employees based on first letter of last name
        employees_by_letter[letter] = []
    employer_legs_n = {}  # totals for each mode
    employer_legs_wr = {}
    info_id = 0
    count = 0 # counts how many individuals don't want their info shared
    for survey in surveys:
        name = survey.name.strip().split(" ")
        if len(name) == 0:
            continue
        elif len(name) >= 2:
            last = name.pop()
            first = name[0]
            if last[0].upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                last_name_starts_with = last[0].upper()
            else:
                continue
        else:
            continue        
        first = first.title()
        last = last.title()      
        if survey.comments != '':
            comments.append(survey.comments)
        legs_n, legs_wr = survey.get_legs()

        [legs_n_objects, legs_wrd_objects] = survey.get_legs_objects()  # for tables

        leg_dirs_n = []
        leg_modes_n = []
        leg_mins_n = []
        leg_kcals_n = []
        leg_carbon_n = []
        leg_dirs_wrd = []
        leg_modes_wrd = []
        leg_mins_wrd = []
        leg_kcals_wrd = []
        leg_carbon_wrd = []

        tw_fw = {'tw': "To Work", 'fw': "From Work"}

        for leg in legs_n_objects:
            leg_dirs_n.append(tw_fw[leg.direction])
            leg_modes_n.append(leg.mode.name)
            leg_mins_n.append(leg.duration)
            leg_kcals_n.append(leg.calories)
            leg_carbon_n.append(leg.carbon)
        for leg in legs_wrd_objects:
            leg_dirs_wrd.append(tw_fw[leg.direction])
            leg_modes_wrd.append(leg.mode.name)
            leg_mins_wrd.append(leg.duration)
            leg_kcals_wrd.append(leg.calories)
            leg_carbon_wrd.append(leg.carbon)

        leg_dirs_n.append("Total")
        leg_modes_n.append(" ")
        leg_mins_n.append(sum(leg_mins_n))
        leg_kcals_n.append(sum(leg_kcals_n))
        leg_carbon_n.append(sum(leg_carbon_n))
        leg_dirs_wrd.append("Total")
        leg_modes_wrd.append(" ")
        leg_mins_wrd.append(sum(leg_mins_wrd))
        leg_kcals_wrd.append(sum(leg_kcals_wrd))
        leg_carbon_wrd.append(sum(leg_carbon_wrd))

        change_choices = {
            'p': 'Positive change',
            'g': 'Green change',
            'h': 'Healthy change',
            'n': 'No change'}

        # Gets rid of -0 carbon/calorie change and incorrect change types for past surveys
        new_change_type = None
        if survey.carbon_change < -0.5:
            if survey.calorie_change > 0.5:
                new_change_type = 'p' # positive change!
            else:
                new_change_type = 'g' # green change
        else:
            if survey.calorie_change > 0.5:
                new_change_type = 'h' # healthy change
            else:
                new_change_type = 'n' # no change

        if new_change_type == 'p' or new_change_type == 'g' or new_change_type == 'h':
            color = "green"
        else:
            color = "black"
        
        info = {'first': first, 'last': last, 'email': survey.email, 'carbon_change': survey.carbon_change,
                'calorie_change': survey.calorie_change, 'change_type': change_choices[new_change_type],
                'id': info_id, 'color': color, 'home_address': survey.home_address}
        info_id += 1
        info['legs_n'], info['legs_wr'] = legs_n, legs_wr
        info["leg_dirs_n"], info["leg_modes_n"], info["leg_mins_n"], info["leg_kcals_n"], info["leg_carbon_n"] = leg_dirs_n, leg_modes_n, leg_mins_n, leg_kcals_n, leg_carbon_n
        info["leg_dirs_wrd"], info["leg_modes_wrd"], info["leg_mins_wrd"], info["leg_kcals_wrd"], info["leg_carbon_wrd"] = leg_dirs_wrd, leg_modes_wrd, leg_mins_wrd, leg_kcals_wrd, leg_carbon_wrd

        # Add to list of people to show in Individual Surveys if they allow their info to be shared

        if not survey.share:
            people = employees_by_letter[last_name_starts_with]  # list of people already in totals_by_letter list starting with first letter of lastname
            people.append(info)
            people.sort(key=lambda x: x['last'])
        else:
            count += 1


        # Add to total statistics for all people (even those who don't want their info shared)
        for legs, employer_legs in [(legs_n, employer_legs_n), (legs_wr, employer_legs_wr)]:
            person_modes = set()  # Keep track of whether or not we added that person to a mode's total # of ppl
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

    employees_by_letter['all'] = []     
    for letter, employees in employees_by_letter.items():
        if letter != 'all':
            employees_by_letter['all'].extend(employees)
    employees_by_letter['all'].sort(key=lambda x: x['last'])

    int_to_str = {1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 6: "june", 7: "july", 8: "august", 9: "september", 10: "october", 11: "november", 12: "december"}
    word_month = int_to_str[int(month)]
    employer_info = calculate_metrics(employer, word_month, year)  # change to current month instead of 'all' and year
    employer_info['total_calories_n'] = employer.total_calories_n(month, year)
    employer_info['total_carbon_n'] = employer.total_C02_n(month, year)
    employer_info['total_carbon'] = employer.total_C02_wr(month, year)
    employer_info['percent_participation'] = employer.percent_participation(month, year)*100
    employer_info['count'] = count
    month_data = {'employer_info': employer_info, 'employees_by_letter': employees_by_letter, 'comments': comments, 'employer_legs_n': employer_legs_n, \
                        'employer_legs_wr': employer_legs_wr, 'question': question}
    return month_data

def save_month_data(employer, month, year,):
    month_data = render_month_data(employer, month, year)
    EmployerMonthInfo.objects.filter(employer_id=employer.id, month=month, year=year).delete()
    EmployerMonthInfo.objects.update_or_create(employer_id=employer.id, month=month, year=year, dict_data=json.dumps(month_data))
    return month_data

def get_month_data(employer, month, year, replace=False):
    if replace:
        return save_month_data(employer, month, year)

    now = datetime.datetime.now()
    try:
        month_info = EmployerMonthInfo.objects.get(employer_id=employer.id, month=month, year=year)
        if year==now.year and (int(month)==now.month or int(month)==now.month-1):
            return save_month_data(employer, month, year)
        else:
            return json.loads(month_info.dict_data)
    except (EmployerMonthInfo.DoesNotExist, EmployerMonthInfo.MultipleObjectsReturned):
        save_month_data(employer, month, year)

# Takes a long time, only call this when database is empty.
def save_all_data(employer=None, replace=False):
    now = datetime.datetime.now()
    short_months = ['04','05','06','07','08','09','10']

    if employer:
        for year in range(2015, now.year+1):
            for month in short_months:
                get_month_data(employer, month, year, replace)
        return True

    employers = Employer.objects.all()
    for employer in employers:
        for year in range(2015, now.year+1):
            for month in short_months:
                get_month_data(employer, month, year, replace)
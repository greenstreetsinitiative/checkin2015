from __future__ import division
from django.db import models
from django.db.models import Sum
from django.core.validators import MaxValueValidator
# unused import: MinValueValidator
import datetime
from datetime import date
from smart_selects.db_fields import ChainedForeignKey
from survey.utils import sanely_rounded

def get_surveys_by_employer(employer, chosenmonth, year):
    if chosenmonth != 'all':
        month_model = Month.objects.filter(wr_day__year=year, wr_day__month=chosenmonth)
        surveys = Commutersurvey.objects.filter(wr_day_month=month_model, employer=employer)
    else:
        elapsed_months = Month.objects.exclude(wr_day__month='01').exclude(wr_day__month='02').exclude(
            wr_day__month='03').exclude(wr_day__month='11').exclude(wr_day__month='12').filter(
            wr_day__year=year, open_checkin__lte=date.today())
        surveys = Commutersurvey.objects.filter(wr_day_month__in=elapsed_months, employer=employer)
    return surveys

def get_surveys_by_team(team, chosenmonth, year):
    if chosenmonth != 'all':
        month_model = Month.objects.filter(wr_day__year=year, wr_day__month=chosenmonth)
        surveys = Commutersurvey.objects.filter(wr_day_month=month_model, team=team)
    else:
        elapsed_months = Month.objects.exclude(wr_day__month='01').exclude(wr_day__month='02').exclude(
            wr_day__month='03').exclude(wr_day__month='11').exclude(wr_day__month='12').filter(
            wr_day__year=year, open_checkin__lte=date.today())
        surveys = Commutersurvey.objects.filter(wr_day_month__in=elapsed_months, team=team)
    return surveys


class Month(models.Model):
    """Walk/Ride Day Months"""
    wr_day = models.DateField('W/R Day Date', null=True)
    open_checkin = models.DateField(null=True)
    close_checkin = models.DateField(null=True)

    class Meta(object):
        ordering = ['wr_day']

    def __unicode__(self):
        return unicode(self.wr_day.strftime('%B %Y'))

    @property
    def short_name(self):
        return self.wr_day.strftime(u'%b\' %y'.encode('utf-8')).decode('utf-8')

    @property
    def month(self):
        return self.wr_day.strftime(u'%B %Y'.encode('utf-8')).decode('utf-8')

class Sector(models.Model):
    """Competing employers are grouped into sectors"""
    name = models.CharField("Sector name", max_length=200)
    short = models.CharField("Sector key", max_length=2)

    def __unicode__(self):
        return unicode(self.name)

class Employer(models.Model):
    """Represents a participating employer"""
    name = models.CharField("Organization name", max_length=200)
    nr_employees = models.PositiveIntegerField(default=1)
    active2015 = models.BooleanField("2015 Challenge", default=False)
    active2016 = models.BooleanField("2016 Challenge", default=False)
    active2017 = models.BooleanField("2017 Challenge", default=False)
    active2018 = models.BooleanField("2018 Challenge", default=False)
    active2019 = models.BooleanField("2019 Challenge", default=False)
    active2020 = models.BooleanField("2020 Challenge", default=False)
    nochallenge = models.BooleanField("Not In Challenge", default=False)
    sector = models.ForeignKey('Sector', null=True, blank=True)


    class Meta(object):
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    def count_checkins(self, shortmonth, year):
        """Calculates and returns number of employees participating"""
        surveys = get_surveys_by_employer(self, shortmonth, year)
        return surveys.count() or 0

    def total_C02(self, shortmonth, year):
        """Calculates and returns total amount of carbon dioxide saved on WR Day (assuming driving on Normal day)"""
        surveys = get_surveys_by_employer(self, shortmonth, year)
        return surveys.aggregate(Sum('carbon_savings')).values()[0] or 0

    def total_calories(self, shortmonth, year):
        """Calculates and returns total calories burned on WR Day"""
        surveys = get_surveys_by_employer(self, shortmonth, year)
        return surveys.aggregate(Sum('calories_total')).values()[0] or 0

    def percent_participation(self, shortmonth, year):
        """Calculates and returns the percentage of employees participating"""
        surveys = get_surveys_by_employer(self, shortmonth, year)
        return surveys.values('email').distinct().count() / self.nr_employees

    def average_percent_participation(self, year):
        """Calculates and returns the percentage of employees participating"""
        elapsed_months = Month.objects.exclude(wr_day__month='01').exclude(wr_day__month='02').exclude(wr_day__month='03').exclude(wr_day__month='11').exclude(wr_day__month='12').filter(
            wr_day__year=year, open_checkin__lte=date.today())

        if (self.nr_employees * elapsed_months.count()) > 0:
            return Commutersurvey.objects.filter(employer=self, wr_day_month__in=elapsed_months).count() / \
                (self.nr_employees * elapsed_months.count())
        else:
            return 0.0

    def percent_already_green(self, shortmonth, year):
        """Calculates and returns the percentage of employees who
        already have a green commute
        """
        surveys = get_surveys_by_employer(self, shortmonth, year)
        already_green = surveys.filter(already_green=True).count()

        if surveys.count() > 0:
            percent = already_green / surveys.count()
        else:
            percent = 0.0
        return percent

    def percent_green_switch(self, shortmonth, year):
        """
        Calculates and returns the % of employees who made a green switch
        """
        surveys = get_surveys_by_employer(self, shortmonth, year)
        green_switch = surveys.filter(change_type__in=['g', 'p']).count()
        if surveys.count() > 0:
            percent = green_switch / surveys.count()
        else:
            percent = 0.0
        return percent

    def percent_healthy_switch(self, shortmonth, year):
        """
        Calculates and returns the % of employees who made a healthy switch
        """
        surveys = get_surveys_by_employer(self, shortmonth, year)
        healthy_switch = surveys.filter(change_type__in=['h', 'p']).count()
        if surveys.count() > 0:
            percent = healthy_switch / surveys.count()
        else:
            percent = 0.0
        return percent


class Team(models.Model):
    """Teams"""
    name = models.CharField("Team", max_length=150)
    parent = models.ForeignKey('Employer')
    nr_members = models.PositiveSmallIntegerField(default=1)

    class Meta(object):
        ordering = ['parent__name', 'name']

    def __unicode__(self):
        return u"%s - %s" % (self.parent.name, self.name)

    def count_checkins(self, shortmonth, year):
        """Calculates and returns number of employees participating"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        return surveys.count()

    def total_C02(self, shortmonth, year):
        """Calculates and returns total amount of carbon dioxide saved on WR Day (assuming driving on Normal day)"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        return surveys.aggregate(Sum('carbon_savings')).values()[0] or 0

    def total_calories(self, shortmonth, year):
        """Calculates and returns total calories burned on WR Day"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        return surveys.aggregate(Sum('calories_total')).values()[0] or 0

    def average_percent_participation(self, year):
        """Calculates and returns the percentage of employees participating"""
        elapsed_months = Month.objects.exclude(wr_day__month='01').exclude(wr_day__month='02').exclude(wr_day__month='03').exclude(wr_day__month='11').exclude(wr_day__month='12').filter(
            wr_day__year=year, open_checkin__lte=date.today())
        return Commutersurvey.objects.filter(team=self, wr_day_month__in=elapsed_months).count() / \
            (self.nr_members * elapsed_months.count())

    def percent_participation(self, shortmonth, year):
        """Calculates and returns the percentage of team employees participating"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        return surveys.values('email').distinct().count() / self.nr_members

    def percent_already_green(self, shortmonth, year):
        """percent of commute already 'green' """
        surveys = get_surveys_by_team(self, shortmonth, year)
        already_green = surveys.filter(already_green=True).count()
        if surveys.count() > 0:
            percent = already_green / surveys.count()
        else:
            percent = 0.0
        return percent

    def percent_green_switch(self, shortmonth, year):
        """change in 'greenness' of commute due to switch"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        green_switch = surveys.filter(change_type__in=['g', 'p']).count()
        if surveys.count() > 0:
            percent = green_switch / surveys.count()
        else:
            percent = 0.0
        return percent

    def percent_healthy_switch(self, shortmonth, year):
        """change in healthiness of commute due to switch"""
        surveys = get_surveys_by_team(self, shortmonth, year)
        healthy_switch = surveys.filter(change_type__in=['h', 'p']).count()
        if surveys.count() > 0:
            percent = healthy_switch / surveys.count()
        else:
            percent = 0.0
        return percent


class Commutersurvey(models.Model):
    """Represents an individual (I think individual) checkin"""
    name = models.CharField("Name", max_length=100, blank=True, null=True)
    wr_day_month = models.ForeignKey('Month')
    home_address = models.CharField("Home address", max_length=300)
    work_address = models.CharField("Workplace address", max_length=300)
    email = models.EmailField("Email address")
    employer = models.ForeignKey('Employer')
    team = models.ForeignKey('Team', null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    questionOne = models.TextField( blank=True, default=None, null=True)
    questionTwo = models.TextField(blank=True, default=None, null=True)
    questionThree = models.TextField(blank=True, default=None, null=True)
    questionFour = models.TextField(blank=True, default=None, null=True)
    questionFive = models.TextField(blank=True, default=None, null=True)

    share = models.BooleanField(
        "Please don't share my identifying information with my employer",
        default=False)
    contact = models.BooleanField("Contact me", default=False)
    volunteer = models.BooleanField('Available to volunteer', default=False)
    created = models.DateTimeField(auto_now_add=True)
    # calculated changes between normal day and walk/ride day
    CHANGE_CHOICES = (
        ('p', 'Positive change'),
        ('g', 'Green change'),
        ('h', 'Healthy change'),
        ('n', 'No change'),
    )

    carbon_change = models.FloatField(blank=True, null=True, default=0.0)
    calorie_change = models.FloatField(blank=True, null=True, default=0.0)
    change_type = models.CharField(max_length=1, null=True, blank=True,
                                   choices=CHANGE_CHOICES)

    # walk/ride day information that will be calculated
    already_green = models.BooleanField(default=False) # if normal day was green
    #carbon savings assumes a normal day is driving
    carbon_savings = models.FloatField(blank=True, null=True, default=0.0)
    # calories burned on w/r day
    calories_total = models.FloatField(blank=True, null=True, default=0.0)

# Not sure how this constraint was being applied to the data.
# The data does not conform.  I am removing it.  In looking at the production
# data it seems that multiple identical records were created at the same time
# Other than through the id field there doesn't seem to be a way to uniquely
# identify duplicate rows. (Gautam, 4/5/2019)

    class Meta:
       unique_together = ("name","email","home_address","work_address", "wr_day_month")

    def __unicode__(self):
        return unicode(self.id)

    def calculate_difference(self):
        """
        Calculates the difference in terms of calories burned and
            carbon emmitted between the commute of this check-in
            on Walk/Ride Day versus their declared normal commute.
        Returns results as a dict, with 'carbon' and 'calories' keyed to
            their changes
        """
        legs = self.leg_set.only('carbon', 'calories', 'day').all()
        difference = {'carbon': 0.000, 'calories': 0.000}
        for leg in legs:
            leg_carbon = leg.carbon*1000 # grams
            leg_calories = leg.calories # kcal
            if leg.day == 'w':
                difference["carbon"] += leg_carbon
                difference["calories"] += leg_calories
            elif leg.day == 'n':
                difference["carbon"] -= leg_carbon
                difference["calories"] -= leg_calories

        return difference

    def change_analysis(self):
        """
        Determines if the change is healthy, green, both or neither.
        Returns results as a single-letter string.
        """
        if self.carbon_change < 0:
            if self.calorie_change > 0:
                return 'p' # positive change!
            else:
                return 'g' # green change
        else:
            if self.calorie_change > 0:
                return 'h' # healthy change
            else:
                return 'n' # no change

    def check_green(self):
        """returns true if any leg on a normal day commute is green."""
        return self.leg_set.filter(day='n', mode__green=True).exists()

    def carbon_saved(self):
        """returns the total carbon saved from all legs in kg"""
        normal_car_carbon = 0.0
        wr_day_carbon = 0.0
        legs = self.leg_set.all()

        # don't calculate if all the legs are driving alone.
#        if legs.filter(day='n').count() == legs.filter(day='n', mode__name="Driving alone").count():
#            return None
        for leg in legs:
            if leg.day == 'n':
                leg_distance = leg.duration/60 * leg.mode.speed # hr * mph = miles
                car_carbon = Mode.objects.get(name="Driving alone").carb/1000 # kilograms carbon per passenger-mile
                leg_car_carbon = car_carbon * leg_distance # kilograms
                normal_car_carbon += leg_car_carbon
            elif leg.day == 'w':
                wr_day_carbon += leg.carbon # kilograms
        carbon_saved = normal_car_carbon - wr_day_carbon
        return sanely_rounded(carbon_saved*1000) # grams

    def calories_totalled(self):
        """Returns the total amount of calories burned due to wrday"""
        wr_day_calories = 0.000
        wr_day_calories = self.leg_set.only('calories').filter(
            day='w').aggregate(Sum('calories'))['calories__sum']
        return wr_day_calories


    def save(self, *args, **kwargs):
        """if there's an existing checkin for this month/email, delete that one and replace it with this checkin"""
        existing_checkin = Commutersurvey.objects.filter(wr_day_month=self.wr_day_month, email=self.email)
        if self.id:
            # if this instance has already been saved we need to filter out this instance from our results.
            existing_checkin = existing_checkin.exclude(pk=self.id)
        if existing_checkin.exists():
            existing_checkin.delete()

        """overwrites the save method in order to calculate all the data!"""
        changes = self.calculate_difference()
        self.carbon_change = sanely_rounded(changes["carbon"])
        self.calorie_change = sanely_rounded(changes["calories"])
        self.change_type = self.change_analysis()
        self.already_green = self.check_green()
        self.carbon_savings = self.carbon_saved()
        self.calories_total = self.calories_totalled()
        super(Commutersurvey, self).save(*args, **kwargs)



class Mode(models.Model):
    """Information on different modes of transportation"""
    name = models.CharField("Mode", max_length=35)
    met = models.FloatField(blank=True, null=True)
    carb = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    green = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.name)


class Leg(models.Model):
    """representation for part of a commute"""
    #FIXME: these look like they want to be enums
    # right now they look like bad C code
    LEG_DIRECTIONS = (
        ('tw', 'to work'),
        ('fw', 'from work'),
    )
    LEG_DAYS = (
        ('w', 'Walk/Ride Day'),
        ('n', 'Normal day'),
    )

    mode = models.ForeignKey('Mode')
    duration = models.PositiveSmallIntegerField(
        default=5, validators=[MaxValueValidator(1440)]) #ensures legs < a day
    direction = models.CharField(max_length=2, choices=LEG_DIRECTIONS)
    day = models.CharField(max_length=1, choices=LEG_DAYS)
    checkin = models.ForeignKey('Commutersurvey')
    carbon = models.FloatField(default=0.0)
    calories = models.FloatField(default=0.0)

    def calc_metrics(self):
        """Calculate the carbon output and calories burned for this leg"""
        calories = 0.0
        carbon = 0.0
        if self.mode:
            met = self.mode.met or 0.0
            carb = self.mode.carb or 0.0
            kcal = float(met) # kcal/(kg*hour) from this mode
            if kcal > 0.0:
                #kcal burned by leg using average weight of 81 kg,
                #based on duration in minutes
                calories = kcal * (self.duration/60) * 80.7
            #grams carbon dioxide per passenger-mile on this mode
            coo = float(carb)
            #grn = self.mode.green
            if coo > 0.0: #and grn<>'f'
                speed = self.mode.speed or 0.0
                s = float(speed) # average speed in mph
                #kilograms carbon expended in leg based on duration in minutes
                carbon = (coo/1000) * s * (self.duration/60)
        return {'carbon': sanely_rounded(carbon), 'calories': sanely_rounded(calories)}

    def save(self, *args, **kwargs):
        """save carbon change"""
        metrics = self.calc_metrics()
        self.carbon = metrics['carbon'] # kilograms
        self.calories = metrics['calories'] # kcal
        super(Leg, self).save(*args, **kwargs)
        #resave the related survey (recalculates carbon and calories)
        self.checkin.save()
    def __unicode__(self):
        return u"%s, %s, %s" % (self.mode, self.day, self.direction)

# Legacy Model used from 2016 to March 2017. Replaced by MonthlyQuestion
class QuestionOfTheMonth(models.Model):
    wr_day_month = models.ForeignKey('Month', blank=True, null=True, default=0)
    value = models.TextField(blank=True, null=True, default='')

    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.wr_day_month)

# This is replacement for QuestionOfTheMonth from April 2017 onwards
class MonthlyQuestion(models.Model):

    wr_day_month = models.ForeignKey('Month', blank=True, null=True, default=0)

    QOM_NUMBER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    questionNumber = models.PositiveIntegerField('Question Number', choices=QOM_NUMBER, default=1)


    QOM_TYPES = (
        (1, 'Select Menu'),
        (2, 'Vertical Radio Buttons'),
        (3, 'Horizontal Radio Buttons'),
        (4, 'Checkboxes'),
        (5, 'Extended Text Response'),
        (6, 'No Response'),
        (7, 'Single Line Text Response'),
    )

    questionType = models.PositiveIntegerField('Type', choices=QOM_TYPES)

    question = models.TextField('Question', default='')


    answer_1 = models.CharField('Answer 1', null=True, max_length=500, blank=True)

    answer_2 = models.CharField('Answer 2', null=True, max_length=500, blank=True)

    answer_3 = models.CharField('Answer 3', null=True, max_length=500, blank=True)

    answer_4 = models.CharField('Answer 4', null=True, max_length=500, blank=True)

    answer_5 = models.CharField('Answer 5', null=True, max_length=500, blank=True)

    answer_6 = models.CharField('Answer 6', null=True, max_length=500, blank=True)

    answer_7 = models.CharField('Answer 7', null=True, max_length=500, blank=True)

    answer_8 = models.CharField('Answer 8', null=True, max_length=500, blank=True)

    answer_9 = models.CharField('Answer 9', null=True, max_length=500, blank=True)

    answer_10 = models.CharField('Answer 10', null=True, max_length=500, blank=True)

    answer_11 = models.CharField('Answer 11', null=True, max_length=500, blank=True)

    answer_12 = models.CharField('Answer 12', null=True, max_length=500, blank=True)

    answer_13 = models.CharField('Answer 13', null=True, max_length=500, blank=True)

    answer_14 = models.CharField('Answer 14', null=True, max_length=500, blank=True)

    answer_15 = models.CharField('Answer 15', null=True, max_length=500, blank=True)



    class Meta:
        ordering = ('wr_day_month','questionNumber')

        unique_together = ("wr_day_month", "questionNumber")

class DonationOrganization(models.Model):
    wr_day_month = models.ForeignKey("survey.month", unique=True, blank=False, null=False)
    organization_name = models.TextField(blank=False, null=False, default='')
    website = models.URLField("Website", blank=True, null=True, default='')

    def __unicode__(self):
        return u"%s (%s)" % (self.organization_name, self.wr_day_month)

from __future__ import division
from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

# Walk/Ride Day Months
class Month(models.Model):
    wr_day = models.DateField('W/R Day Date', null=True)
    open_checkin = models.DateField(null=True)
    close_checkin = models.DateField(null=True)

    class Meta:
        ordering = ['wr_day']

    def __unicode__(self):
        return unicode(self.wr_day.strftime('%B %Y'))

    @property
    def short_name(self):
        return self.wr_day.strftime(u'%b\' %y'.encode('utf-8')).decode('utf-8')

    @property
    def month(self):
        return self.wr_day.strftime(u'%B %Y'.encode('utf-8')).decode('utf-8')

class Employer(models.Model):
    name = models.CharField("Organization name", max_length=200)
    nr_employees = models.PositiveIntegerField(default=1)
    active2015 = models.BooleanField("2015 Challenge", default=False)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    def percent_participation(self):
        return Commutersurvey.objects.filter(employer=self).distinct('email').count() / self.nr_employees

    def percent_already_green(self):
        surveys = Commutersurvey.objects.filter(employer=self)
        already_green = surveys.filter(already_green=True).count()
        percent = already_green / surveys.count()
        return percent

    def percent_green_switch(self):
        surveys = Commutersurvey.objects.filter(employer=self)
        green_switch = surveys.filter(change_type__in=['g','p']).count()
        percent = green_switch / surveys.count()
        return percent

    def percent_healthy_switch(self):
        surveys = Commutersurvey.objects.filter(employer=self)
        healthy_switch = surveys.filter(change_type__in=['h','p']).count()
        percent = healthy_switch / surveys.count()
        return percent

# Teams
class Team(models.Model):
    name = models.CharField("Team", max_length=150)
    parent = models.ForeignKey('Employer')
    nr_members = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['parent__name', 'name']

    def __unicode__(self):
        return unicode(self.parent.name + ' - ' + self.name)

# Checkins
class Commutersurvey(models.Model):
    name = models.CharField("Full name", max_length=100, blank=True, null=True)
    wr_day_month = models.ForeignKey('Month')
    home_address = models.CharField("Home address", max_length=300)
    work_address = models.CharField("Work address", max_length=300)
    email = models.EmailField("Work email address")
    employer = models.ForeignKey('Employer')
    team = models.ForeignKey('Team', null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    share = models.BooleanField("Please don't share my identifying information with my employer", default=False)
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
    change_type = models.CharField(max_length=1, null=True, blank=True, choices=CHANGE_CHOICES)

    # walk/ride day information that will be calculated
    already_green = models.BooleanField(default=False) # if normal day was green
    carbon_savings = models.FloatField(blank=True, null=True, default=0.0) # assuming normal day is driving
    calories_total = models.FloatField(blank=True, null=True, default=0.0) # calories burned on w/r day

    def __unicode__(self):
        return unicode(self.id)

    def calculate_difference(self):
        legs = self.leg_set.only('carbon','calories','day').all()

        difference = {'carbon': 0.000, 'calories': 0.000 }

        for leg in legs:
            if leg.day == 'w':
                difference["carbon"] += leg.carbon
                difference["calories"] += leg.calories
            elif leg.day == 'n':
                difference["carbon"] -= leg.carbon
                difference["calories"] -= leg.calories

        return difference

    def change_analysis(self):
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
        # if any leg on a normal day commute is green
        return self.leg_set.filter(day='n',mode__green=True).exists()

    def carbon_saved(self):
        normal_car_carbon = 0.0
        wr_day_carbon = 0.0

        legs = self.leg_set.only('carbon','day').all()

        for leg in legs:
            if leg.day == 'n':
                car_speed = Mode.objects.get(name="Driving alone").speed
                car_carbon = Mode.objects.get(name="Driving alone").carb/1000
                carbon = car_carbon * car_speed * leg.duration/60
                normal_car_carbon += carbon
            elif leg.day == 'w':
                wr_day_carbon += leg.carbon

        carbon_saved = wr_day_carbon - normal_car_carbon

        return carbon_saved

    def calories_totalled(self):
        wr_day_calories = 0.0
        wr_day_calories = self.leg_set.only('calories').filter(day='w').aggregate(Sum('calories'))['calories__sum']
        return wr_day_calories

    # overwrite the save method so we can calculate all the data!
    def save(self, *args, **kwargs):
        changes = self.calculate_difference()
        self.carbon_change = changes["carbon"]
        self.calorie_change = changes["calories"]
        self.change_type = self.change_analysis()
        self.already_green = self.check_green()
        self.carbon_savings = self.carbon_saved()
        self.calories_total = self.calories_totalled()
        super(Commutersurvey, self).save(*args, **kwargs)

# Information on different modes of transportation
class Mode(models.Model):
    name = models.CharField("Mode", max_length=35)
    met = models.FloatField(blank=True, null=True)
    carb = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    green = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.name)

# Part of a commute
class Leg(models.Model):

    LEG_DIRECTIONS = (
        ('tw', 'to work'),
        ('fw', 'from work'),
    )

    LEG_DAYS = (
        ('w', 'Walk/Ride Day'),
        ('n', 'Normal day'),
    )

    mode = models.ForeignKey('Mode')
    duration = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(5),MaxValueValidator(1440)]) # ensures legs are longer than 5 minutes and shorter than a day
    direction = models.CharField(max_length=2, choices=LEG_DIRECTIONS)
    day = models.CharField(max_length=1, choices=LEG_DAYS)
    checkin = models.ForeignKey('Commutersurvey')
    carbon = models.FloatField(default=0.0)
    calories = models.FloatField(default=0.0)

    def calc_metrics(self):
        calories = 0.0
        carbon = 0.0

        if self.mode:
            kcal = float(self.mode.met) # kcal/(kg*hour) from this mode

            if kcal > 0.0:
                # amount of calories (kcal) burned by this leg using average American weight of 81 kg based on a duration in minutes
                calories = kcal * (self.duration/60) * 81

            coo = float(self.mode.carb) # grams carbon dioxide per passenger-mile on this mode

            if coo > 0.0:

                s = float(self.mode.speed) # average speed of this mode in mph

                # amount of carbon in kilograms expended by this leg based on a duration in minutes
                carbon = (coo/1000) * s * (self.duration/60)

        return {'carbon': carbon, 'calories': calories }

    def save(self, *args, **kwargs):
        # save carbon change
        metrics = self.calc_metrics()
        self.carbon = metrics['carbon']
        self.calories = metrics['calories']
        super(Leg, self).save(*args, **kwargs)

        self.checkin.save() # resave the related survey (recalculates carbon and calories)

    def __unicode__(self):
        return unicode(self.mode)


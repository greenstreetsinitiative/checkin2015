import models
import utils
import datetime

from itertools import cycle
from random import randint

from django.test import TestCase, Client, RequestFactory
from django.conf import settings
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from views import add_checkin


class SessionTestCase(TestCase):
    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        
class CheckinViewTestCase(SessionTestCase):
    fixtures = ['modes.json']

    def setUp(self):
        super(CheckinViewTestCase, self).setUp()
        fixtures = Fixtures()
        fixtures.create_employer()
        fixtures.create_legs()

    def test_email_validation(self):
        When(self).submitting_a_survey.with_all_the_fields.except_for(email='').the_result.should.contain('Please enter an email')
        When(self).submitting_a_survey.with_all_the_fields.the_result.should_not.contain('Please enter an email')
    
    def test_successful_submission(self):
        nb_surveys_before = len(models.Commutersurvey.objects.all())
        nb_legs_before = len(models.Leg.objects.all())

        When(self).submitting_a_survey.logged_as("Bob").with_all_the_fields. \
        the_result.should_not.contain('Oops').should.contain("Thank you, Bob")

        nb_surveys_after = len(models.Commutersurvey.objects.all())
        nb_legs_after = len(models.Leg.objects.all())
        
        self.assertEqual(nb_surveys_before+1, nb_surveys_after, "1 Commutersurvey should have been created")
        self.assertEqual(nb_legs_before+4, nb_legs_after, "4 legs should have been created")

    def test_session_populates_form(self):
        utils.this_month()
        s = self.session
        s["name"] = 'Bob'
        s.save()
        response = self.client.get('/checkin/', follow=True)
        self.assertEqual(response.context['form']['name'].value(), 'Bob')

    def test_checkin_subteam_warning(self):
        warning = "Your company has participating sub-teams! Please indicate your team affiliation above."
        response = self.client.get('/checkin/', follow=True)
        self.assertNotContains(response, warning)

        #e = mommy.make(models.Employer)
        e = models.Employer.objects.get(pk=1)
        e.team_set.create(name='Team1')
        e.team_set.create(name='Team2')
        e.team_set.create(name='Team3')

        # this won't work. need a liveserver test case?
        #When(self).submitting_a_survey.logged_as("Bob").with_all_the_fields. \
        #the_result.should.contain(warning)

    def test_complete_page_advises_private(self):
        message = "Open in an incognito or private window"
        response = self.client.get('/checkin/complete/', follow=True)
        self.assertContains(response, message)

        
class ModeTests(TestCase):

    def setUp(self):
        models.Mode.objects.create(name="bike", met=50.0,
                                   carb=0.0, speed=20.0, green=True)

    def test_create_mode(self):
        bike = models.Mode.objects.get(name='bike')
        self.assertEqual(bike.name, 'bike')
        self.assertEqual(bike.speed, 20.0)
        self.assertEqual(bike.carb, 0.0)
        self.assertEqual(bike.met, 50.0)
        self.assertEqual(bike.green, True)

        
class LegTests(TestCase):

    fixtures = ['modes.json']

    def setUp(self):
        fixtures = Fixtures()
        self.leg_recipe, self.checkin = fixtures.create_legs()

    def decimal_places(self, number):
        # converts to string, reverses it, and finds where the decimal point is
        return repr(number)[::-1].find('.')

    def test_leg_model_calculations_up_to_3_decimal_places(self):
        # no one leg will both expend carbon and burn calories. so use two legs.
        carpool_leg = self.leg_recipe.make(mode=models.Mode.objects.get(pk=3))
        running_leg = self.leg_recipe.make(mode=models.Mode.objects.get(pk=11))
        self.assertLessEqual(self.decimal_places(carpool_leg.carbon), 3)
        self.assertLessEqual(self.decimal_places(carpool_leg.calories), 3)
        self.assertLessEqual(self.decimal_places(running_leg.carbon), 3)
        self.assertLessEqual(self.decimal_places(running_leg.calories), 3)

    def test_commutersurvey_model_calculations_up_to_3_decimal_places(self):
        self.assertLessEqual(self.decimal_places(self.checkin.carbon_change), 3)
        self.assertLessEqual(self.decimal_places(self.checkin.calorie_change), 3)
        self.assertLessEqual(self.decimal_places(self.checkin.carbon_savings), 3)
        self.assertLessEqual(self.decimal_places(self.checkin.calories_total), 3)

####################################################################
# Helper classes
####################################################################

# Helper class to create fixtures for the Employer and Leg classes
class Fixtures:
    def create_employer(self):
        emp = models.Employer.objects.create(name="ACME", id=1, nochallenge=True, active2015=True, active2016=True)
        emp.save()
    
    def leg_setup(self):
        self.survey_recipe = Recipe(models.Commutersurvey)
        self.all_modes = models.Mode.objects.all()
        self.leg_recipe = Recipe(
            models.Leg,
            checkin = self.survey_recipe.make(),
            mode = cycle(self.all_modes)
        )

    def generate_leg_set(self, checkin):
        # generates a set of legs to associate with a given checkin
        # set is complete in the sense of having 1+ leg per direction/day pair
        self.leg_recipe.make(day='w', direction='fw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='w', direction='tw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='n', direction='fw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='n', direction='tw', checkin=checkin, _quantity=randint(1,3))

    def create_legs(self):
        self.leg_setup()
        checkin = self.survey_recipe.make()
        self.generate_leg_set(checkin)
        checkin.save()
        return (self.leg_recipe, checkin)

# Helper class that encapsulates tests
class When:
    def __init__(self, parent):
        self.parent = parent
        self.factory = RequestFactory()

    @property
    def submitting_a_survey(self):
        utils.this_month()
        
        self.request = self.factory.post(reverse('commuterform'), follow=True)
        self.request.session = self.parent.session
        return self

    def logged_as(self, name):
        s = self.parent.session
        s["name"] = name
        s.save()
        return self
    
    @property
    def with_all_the_fields(self):
        self.request.POST = {
            'name': 'Bob',
            'email': 'test@test.com',
            'home_address': '123 Boston St, Salem, MA 01970, USA',
            'work_address': '124 Boston St, Salem, MA 01970, USA',
            'employer': '1',
            'team': '',
            'ntw-TOTAL_FORMS': '1',
            'ntw-INITIAL_FORMS': '0',
            'ntw-MIN_NUM_FORMS': '0',
            'ntw-MAX_NUM_FORMS': '10',
            'nfw-TOTAL_FORMS': '1',
            'nfw-INITIAL_FORMS': '0',
            'nfw-MIN_NUM_FORMS': '0',
            'nfw-MAX_NUM_FORMS': '10',
            'wtw-TOTAL_FORMS': '1',
            'wtw-INITIAL_FORMS': '0',
            'wtw-MIN_NUM_FORMS': '0',
            'wtw-MAX_NUM_FORMS': '10',
            'wfw-TOTAL_FORMS': '1',
            'wfw-INITIAL_FORMS': '0',
            'wfw-MIN_NUM_FORMS': '0',
            'wfw-MAX_NUM_FORMS': '10',
            'wtw-0-mode': '1',
            'wtw-0-duration': '5',
            'wtw-0-DELETE': '',
            'wtw-0-day': 'w',
            'wtw-0-direction': 'tw',
            'wtw-0-id': '',
            'wtw-0-checkin': '',
            'walkride_same_as_reverse': 'True',
            'wfw-0-mode': '1',
            'wfw-0-duration': '5',
            'wfw-0-DELETE': '',
            'wfw-0-day': 'w',
            'wfw-0-direction': 'fw',
            'wfw-0-id': '',
            'wfw-0-checkin': '',
            'normal_same_as_walkride': 'True',
            'ntw-0-mode': '1',
            'ntw-0-duration': '5',
            'ntw-0-DELETE': '',
            'ntw-0-day': 'n',
            'ntw-0-direction': 'tw',
            'ntw-0-id': '',
            'ntw-0-checkin': '',
            'normal_same_as_reverse': 'True',
            'nfw-0-mode': '1',
            'nfw-0-duration': '5',
            'nfw-0-DELETE': '',
            'nfw-0-day': 'n',
            'nfw-0-direction': 'fw',
            'nfw-0-id': '',
            'nfw-0-checkin': '',
            'comments': '',
            'action': 'action'
        }
        return self
        
    def except_for(self, **kwargs):
        for key, val in kwargs.iteritems():
            self.request.POST[key] = val
        return self

    @property
    def the_result(self):
        self.response = add_checkin(self.request)
        return self
        
    @property
    def should(self):
        self.condition = True
        return self
        
    @property
    def should_not(self):
        self.condition = False
        return self
        
    def contain(self, text):
        if self.condition:
            self.parent.assertContains(self.response, text)
        else:
            self.parent.assertNotContains(self.response, text)
        return self
    
    def debug(self):
        print(self.response)
        return self

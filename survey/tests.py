from django.test import TestCase, Client
from django.conf import settings
from django.utils.importlib import import_module
import models
import utils
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from itertools import cycle
from random import randint
import datetime

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

    def test_session_populates_form(self):
        utils.this_month()
        s = self.session
        s["name"] = 'Bob'
        s.save()
        response = self.client.get('/checkin/', follow=True)
        self.assertEqual(response.context['form']['name'].value(), 'Bob')

    def test_checkin_subteam_warning(self):
        warning = "Your company has sub-teams! Please indicate your team affiliation above."
        response = self.client.get('/checkin/', follow=True)
        self.assertNotContains(response, warning)

        e = mommy.make(models.Employer)
        e.team_set.create(name='Team1')
        e.team_set.create(name='Team2')
        e.team_set.create(name='Team3')

        # this won't work. need a liveserver test case?
        # https://docs.djangoproject.com/en/1.7/topics/testing/tools/#django.test.LiveServerTestCase
        # response_post = self.client.post('/checkin/', {
        #     'name': 'Fname Lname',
        #     'email': 'example@email.com',
        #     'home_address': '123 Residential St., City, ST 12345',
        #     'work_address': '987 Business Ave., OtherCity, ST 12354',
        #     'employer': e,
        #     'team': '',
        #     'wtw-TOTAL_FORMS': 1,
        #     'wtw-INITIAL_FORMS': 0,
        #     'wfw-TOTAL_FORMS': 1,
        #     'wfw-INITIAL_FORMS': 0,
        #     'ntw-TOTAL_FORMS': 1,
        #     'ntw-INITIAL_FORMS': 0,
        #     'nfw-TOTAL_FORMS': 1,
        #     'nfw-INITIAL_FORMS': 0,
        #     'walkride_same_as_reverse': 'True',
        #     'normal_same_as_walkride': 'False',
        #     'normal_same_as_reverse': 'False',
        #     'wtw-MIN_NUM_FORMS': 0,
        #     'wtw-MAX_NUM_FORMS': 10,
        #     'wfw-MIN_NUM_FORMS': 0,
        #     'wfw-MAX_NUM_FORMS': 10,
        #     'ntw-MIN_NUM_FORMS': 0,
        #     'ntw-MAX_NUM_FORMS': 10,
        #     'nfw-MIN_NUM_FORMS': 0,
        #     'nfw-MAX_NUM_FORMS': 10
        # }, follow=True)
        #
        # self.assertContains(response, warning)

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
        self.survey_recipe = Recipe(models.Commutersurvey)
        self.all_modes = models.Mode.objects.all()
        self.leg_recipe = Recipe(
            models.Leg,
            checkin = self.survey_recipe.make(),
            mode = cycle(self.all_modes)
        )

    def decimal_places(self, number):
        # converts to string, reverses it, and finds where the decimal point is
        return repr(number)[::-1].find('.')

    def generate_leg_set(self, checkin):
        # generates a set of legs to associate with a given checkin
        # set is complete in the sense of having 1+ leg per direction/day pair
        self.leg_recipe.make(day='w', direction='fw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='w', direction='tw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='n', direction='fw', checkin=checkin, _quantity=randint(1,3))
        self.leg_recipe.make(day='n', direction='tw', checkin=checkin, _quantity=randint(1,3))

    def test_leg_model_calculations_up_to_3_decimal_places(self):
        # no one leg will both expend carbon and burn calories. so use two legs.
        carpool_leg = self.leg_recipe.make(mode=models.Mode.objects.get(pk=3))
        running_leg = self.leg_recipe.make(mode=models.Mode.objects.get(pk=11))
        self.assertLessEqual(self.decimal_places(carpool_leg.carbon), 3)
        self.assertLessEqual(self.decimal_places(carpool_leg.calories), 3)
        self.assertLessEqual(self.decimal_places(running_leg.carbon), 3)
        self.assertLessEqual(self.decimal_places(running_leg.calories), 3)

    def test_commutersurvey_model_calculations_up_to_3_decimal_places(self):
        checkin = self.survey_recipe.make()
        self.generate_leg_set(checkin)
        checkin.save()

        self.assertLessEqual(self.decimal_places(checkin.carbon_change), 3)
        self.assertLessEqual(self.decimal_places(checkin.calorie_change), 3)
        self.assertLessEqual(self.decimal_places(checkin.carbon_savings), 3)
        self.assertLessEqual(self.decimal_places(checkin.calories_total), 3)

class QOTMTests(TestCase):
    def test_create_qotm(self):
        m = utils.this_month()
        question = "What do you think about bikes?"
        q = models.QuestionOfTheMonth.objects.create(wr_day_month=m, value=question)
        self.assertEqual(q.wr_day_month, m)
        self.assertEqual(q.value, "What do you think about bikes?")

    def test_current_month_question_shown(self):
        before = datetime.datetime.now() - datetime.timedelta(days=32)
        after = datetime.datetime.now() + datetime.timedelta(days=32)
        last_month = models.Month.objects.create(
            wr_day = before,
            open_checkin = before - datetime.timedelta(days=3),
            close_checkin = before + datetime.timedelta(days=3))
        next_month = models.Month.objects.create(
            wr_day = after,
            open_checkin = after - datetime.timedelta(days=3),
            close_checkin = after + datetime.timedelta(days=3))

        models.QuestionOfTheMonth.objects.create(
            wr_day_month=last_month,
            value='Why is transit important?')
        models.QuestionOfTheMonth.objects.create(
            wr_day_month=utils.this_month(),
            value='When will the DC Metro stop catching fire?')
        models.QuestionOfTheMonth.objects.create(
            wr_day_month=next_month,
            value='How many tradeoffs does the state DOT make when budgeting?')

        response = self.client.get('/checkin/', follow=True)
        self.assertContains(response, 'When will the DC Metro stop catching fire?')

from django.test import TestCase
import models
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from itertools import cycle
from random import randint

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

    def decimal_place_index(self, number):
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
        self.assertLessEqual(self.decimal_place_index(carpool_leg.carbon), 3)
        self.assertLessEqual(self.decimal_place_index(carpool_leg.calories), 3)
        self.assertLessEqual(self.decimal_place_index(running_leg.carbon), 3)
        self.assertLessEqual(self.decimal_place_index(running_leg.calories), 3)

    def test_commutersurvey_model_calculations_up_to_3_decimal_places(self):
        checkin = self.survey_recipe.make()
        self.generate_leg_set(checkin)
        checkin.save()

        self.assertLessEqual(self.decimal_place_index(checkin.carbon_change), 3)
        self.assertLessEqual(self.decimal_place_index(checkin.calorie_change), 3)
        self.assertLessEqual(self.decimal_place_index(checkin.carbon_savings), 3)
        self.assertLessEqual(self.decimal_place_index(checkin.calories_total), 3)

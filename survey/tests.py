from django.test import TestCase
import models


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

    pass

from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse

import datetime
import string
import random


def id_generator(size=15, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def randomString(request):

	now = datetime.datetime.now()

	greeting = "Morning"

	hour = now.strftime('%H')

	dateInfo = now.strftime('%I:%M%p on %Y-%m-%d')

	hour = int(hour)

	if hour > 11:
		greeting = "afternoon"

	if hour > 17: 
		greeting = "evening"

	if hour < 3: 
		greeting = "evening"

	return HttpResponse("<html><head><title>Random String</title></head><body><p>Good " + greeting + ", it's " + dateInfo + ".</p>" +"<p>Random String: " +    id_generator() + "</p></body></html>")
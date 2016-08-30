from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from retail.models import partner

from django.core.validators import URLValidator, validate_email
from django.core.exceptions import ValidationError

import json, re, urllib2

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError

phoneRE = re.compile(r'(?:\()?\d{3}(?:-|\s|\.|\)\s|\))?\d{3}(?:-|\.|\s)?\d{4}')
mobileRE = re.compile(r'Android(?=.*Mobile)|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini')  # android tablets don't contain 'mobile' in their user agents,
                                                # but android phones do
tabletRE = re.compile(r'Android|Windows(?=.*Touch)|iPad')

# Create your views here.
def index(request):
  if request.method == 'GET':
    partners = partner.objects.filter(approved=True).order_by('name')
    template = loader.get_template('retail/index.html')

    if mobileRE.search(request.META.get('HTTP_USER_AGENT')):
      isMobile = True
    else:
      isMobile = False

    if tabletRE.search(request.META.get('HTTP_USER_AGENT')) and not isMobile:
      isTablet = True
    else:
      isTablet = False

    context = RequestContext(request, {
      'partners': partners,
      'isMobile': isMobile,
      'isTablet': isTablet
    })

    return HttpResponse(template.render(context))

  if request.method == 'POST':
    try: # to obtain data
      data = request.POST.get('formJSON', '')
      data = json.loads(data)
    except:
      return HttpResponse(json.dumps({'success':False, 'message':'Unable to get user data.'}))

    errors = {} # Dict to store error messages
    errors['data'] = data
    errors['issues'] = []

    # Business name
    try:
      name = data['name']
    except:
      errors['issues'].append('Missing business name')

    # Business website
    try:
      website = data['website']
      try:
        if 'http://' not in website and 'https://' not in website:
          website = 'http://' + website
        URLValidator()(website)
      except ValidationError:
        errors['issues'].append('Invalid business website')
    except:
      errors['issues'].append('Missing business website')

    # Business phone number
    try:
      phone = data['phone']
      try:
        if not phoneRE.match(phone):
          raise ValueError
      except ValueError:
        errors['issues'].append('Business phone is invalid')
    except:
      errors['issues'].append('Missing business phone number')

    # Business address
    try:
      url = "http://www.mapquestapi.com/geocoding/v1/address?"
      url += 'key=' + settings.MAPQUEST_API_KEY + '&'
      url += 'inFormat=kvp&'
      url += 'outputFormat=json&'
      url += 'location=' + data['address'].replace(' ','%20') + '&'
      url += 'thumbMaps=false'

      try: # Geocode address using mapquest
        u = urllib2.urlopen(url).read()
        j = json.loads(u)
        latitude = j['results'][0]['locations'][0]['latLng']['lat']
        longitude = j['results'][0]['locations'][0]['latLng']['lng']
        street = j['results'][0]['locations'][0]['street'].strip()
        city = j['results'][0]['locations'][0]['adminArea5'].strip()
        zipcode = j['results'][0]['locations'][0]['postalCode'][0:5].strip()
      except:
        errors['issues'].append('Unable to locate address, likely invalid')

    except:
      url = ''
      errors['issues'].append('Missing business address')

    # Offer
    try:
      offer = data['offer']
    except:
      errors['issues'].append('Missing offer information')

    # Contact name
    try:
      contact_name = data['contact_name']
    except:
      errors['issues'].append('Missing contact name')

    # Contact Phone
    try:
      contact_phone = data['contact_phone']
      try:
        if not phoneRE.match(contact_phone):
          raise ValueError
      except ValueError:
        errors['issues'].append('Invalid contact phone number')
    except:
      errors['issues'].append('Missing contact phone number')

    # Contact email
    try:
      contact_email = data['contact_email']
      try:
        validate_email(contact_email)
      except ValidationError:
        errors['issues'].append('Invalid contact e-mail')
    except:
      errors['issues'].append('Missing contact e-mail')

    # If data is validate just fine, save to database
    if not errors['issues']:
      p = partner(name=name,phone=phone,website=website,street=street,city=city,zipcode=zipcode,latitude=latitude,longitude=longitude,offer=offer,category='None',contact_name=contact_name,contact_phone=contact_phone,contact_email=contact_email,notes='',approved=False)
      p.save()
      send_email(True)
      return HttpResponse(json.dumps({'success':True}), content_type="application/json")
    else:
      send_email(False, json.dumps(errors, indent=4))
      return HttpResponse(json.dumps({'success':False, 'message': errors}), content_type="application/json")

  else:
    return HttpResponse('Request method not accepted.')

def send_email(success, dump=None):
    if success:
        subject = ('New retail partner!')
        message = (
            'A new retail partner application was submitted.\nhttp://checkinapp-greenstreets.rhcloud.com/admin/retail/partner')
    else:
        subject = ('Attempted new retail partner; failure')
        message = dump
    recipient_list = ['info@gogreenstreets.org','gustavo@gogreenstreets.org']
    from_email = 'retailpartners@gogreenstreets.org'
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)

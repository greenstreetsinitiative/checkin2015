from django.db import models


class partner(models.Model):
    # Business Information
    name = models.TextField()
    phone = models.CharField(max_length=32, null=True, blank=True)
    website = models.CharField(max_length=2048, null=True, blank=True)

    # Address / Location
    street = models.TextField()
    city = models.TextField()
    zipcode = models.CharField(max_length=6)

    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    # Deal information
    offer = models.TextField()
    category = models.CharField(max_length=32, default='None', null=True,
                                blank=True)

    # Contact Information
    contact_name = models.TextField(null=True, blank=True)
    contact_phone = models.TextField(null=True, blank=True)
    contact_email = models.TextField(null=True, blank=True)

    # Additional notes
    notes = models.TextField(null=True, blank=True)

    # Boolean value to determine whether or not to display this retail partner
    approved = models.BooleanField(default=False)

    def phoneNumber(self):
        return '({0}) {1}-{2}'.format(self.phone[0:3], self.phone[3:6],
                                      self.phone[6:])

    def contactPhoneNumber(self):
        if (self.contact_phone):
            if len(self.contact_phone) == 10:
                return '({0}) {1}-{2}'.format(self.contact_phone[0:3],
                                              self.contact_phone[3:6],
                                              self.contact_phone[6:10])
            else:
                return self.contact_phone
        else:
            return ''

    def address(self):
        return self.street + ', ' + self.city + ', MA ' + self.zipcode

    def __unicode__(self):
        return u'%s' % (self.name)

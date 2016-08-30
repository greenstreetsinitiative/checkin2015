from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from retail.models import partner, event

import csv
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
    writer = csv.writer(response)

    field_names = [field.name for field in opts.fields]

    # Write a first row with header information
    writer.writerow(field_names)

    # Write data rows
    for obj in queryset:
        try:
            writer.writerow([getattr(obj, field) for field in field_names])
        except UnicodeEncodeError:
            print "Could not export data row."
    return response

export_as_csv.short_description = "Export selected retailers as csv file"


def approve_selected(modeladmin, request, queryset):
    queryset.update(approved=True)

approve_selected.short_description = "Approve selected"


def disapprove_selected(modeladmin, request, queryset):
    queryset.update(approved=False)

disapprove_selected.short_description = "Disapprove selected"


# Register your models here.
class partnerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Business Information', {'fields': ['name', 'phone', 'website',
                                  'offer']}),
        ('Address', {'fields': ['street', 'city', 'zipcode']}),
        ('Coordinates', {'fields': ['latitude', 'longitude']}),
        ('Contact Information', {'fields': ['contact_name', 'contact_phone',
                                            'contact_email']}),
        ('Other', {'fields': ['category', 'notes']}),
        (None, {'fields': ['approved']})
    ]

    list_display = ('name', 'address', 'contact_name', 'contactPhoneNumber',
                    'contact_email', 'notes', 'approved')
    list_filter = ['approved', 'city']
    search_fields = ['name']
    list_per_page = 200
    actions = ['delete_selected', export_as_csv, approve_selected,
               disapprove_selected]

admin.site.register(partner, partnerAdmin)


class EventActiveFilter(admin.SimpleListFilter):
    title = _('Event Active')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'event_active'

    def lookups(self, request, model_admin):
        return (
            ('Upcoming', _('Upcoming events')),
            ('Past', _('Past events')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Upcoming':
            return queryset.filter(date__gte=datetime.now())
        if self.value() == 'Past':
            return queryset.filter(date__lt=datetime.now())


class eventAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Event Information', {'fields': ['name', 'phone', 'website',
                                          'description', 'date']}),
        ('Address', {'fields': ['street', 'city', 'zipcode']}),
        ('Coordinates', {'fields': ['latitude', 'longitude']}),
        ('Contact Information', {'fields': ['contact_name', 'contact_phone',
                                            'contact_email']}),
        ('Other', {'fields': ['notes']}),
        (None, {'fields': ['approved']})
    ]

    list_display = ('name', 'event_day', 'event_time',
                    'address', 'contact_name', 'contact_phone_number',
                    'contact_email', 'notes', 'approved')
    list_filter = ['approved', 'city', EventActiveFilter]
    search_fields = ['name']
    list_per_page = 200
    actions = ['delete_selected', export_as_csv,
               approve_selected, disapprove_selected]

admin.site.register(event, eventAdmin)

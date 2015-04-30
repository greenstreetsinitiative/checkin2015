from django.contrib import admin

from retail.models import partner

import csv
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

def export_as_csv(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
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

approve_selected.short_description = "Approve selected retailers."

def disapprove_selected(modeladmin, request, queryset):
    queryset.update(approved=False)

disapprove_selected.short_description = "Disapprove selected retailers."


# Register your models here.
class partnerAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Business Information',  {'fields' : ['name', 'phone', 'website', 'offer']}),
    ('Address',         {'fields' : ['street', 'city', 'zipcode']}),
    ('Coordinates',       {'fields' : ['latitude', 'longitude']}),
    ('Contact Information',   {'fields' : ['contact_name', 'contact_phone', 'contact_email']}),
    ('Other',           {'fields' : ['category', 'notes']}),
    ( None,           {'fields' : ['approved']})
  ]

  list_display = ('name', 'address', 'contact_name', 'contactPhoneNumber', 'contact_email', 'notes', 'approved')
  list_filter = ['approved', 'city']
  search_fields = ['name']
  list_per_page = 200
  actions = ['delete_selected', export_as_csv, approve_selected, disapprove_selected]

admin.site.register(partner, partnerAdmin)
from django.contrib import admin

# Register your models here.

import csv
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Sum, Count

from django.forms import ModelForm

from survey.models import Commutersurvey, Employer, Leg, Month, Mode, Team

# disable deletion of records
admin.site.disable_action('delete_selected')

def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """

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

export_as_csv.short_description = "Export selected rows as csv file"

class EmployerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display_links = ['id']
    list_display = ['id', 'name', 'active2015', 'nr_employees']
    list_editable = ['name', 'nr_employees']
    actions = [export_as_csv]

class CommutersurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
            {'fields': ['wr_day_month', 'name', 'email', 'employer', 'share', 'comments', ]}),
        ('Commute',
            {'fields': ['home_address', 'work_address']})
    ]
    list_display = ('id', 'wr_day_month', 'email', 'name', 'share', 'employer', 'home_address', 'work_address', 'carbon_change', 'calorie_change' )
    list_filter = ['wr_day_month', 'employer', 'share', 'volunteer']
    search_fields = ['name', 'email', 'employer__name']
    actions = [export_as_csv]

class LegAdmin(admin.ModelAdmin):
    list_display = ['id', 'direction', 'day', 'checkin', 'mode', 'duration', 'carbon', 'calories']
    list_filter = ('checkin__wr_day_month', 'mode__name')
    actions = [export_as_csv]

    # show only legs from companies active in 2015
    def get_queryset(self, request):
        qs = super(LegAdmin, self).get_queryset(request)
        return qs.filter(commutersurvey__employer__active2015=True)

class MonthAdmin(admin.ModelAdmin):
    list_display = ['id', 'wr_day', 'open_checkin', 'close_checkin']
    list_editable = ['wr_day', 'open_checkin', 'close_checkin']
    actions = [export_as_csv]

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'nr_members']
    list_editable = ['name', 'parent', 'nr_members']
    actions = [export_as_csv]

    # only show 2015 employers for team admin
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Employer.objects.filter(active2015=True)
        return super(TeamAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ModeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'met', 'carb', 'speed', 'green' ]
    list_editable = ['name', 'met', 'carb', 'speed', 'green']
    actions = [export_as_csv]


admin.site.register(Commutersurvey, CommutersurveyAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Month, MonthAdmin)
admin.site.register(Leg, LegAdmin)
admin.site.register(Mode, ModeAdmin)
admin.site.register(Team, TeamAdmin)

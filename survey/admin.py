from django.contrib import admin

# Register your models here.

import csv
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Sum, Count

from django.forms import ModelForm

from survey.models import Commutersurvey, Employer, Leg, Month, Mode, Team, Sector, QuestionOfTheMonth

# disable deletion of records
admin.site.disable_action('delete_selected')

def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """

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

export_as_csv.short_description = "Export selected rows as csv file"

class EmployerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display_links = ['id']
    list_display = ['id', 'name', 'sector', 'nochallenge', 'active2015', 'active2016', 'nr_employees']
    list_editable = ['name', 'sector', 'nr_employees', 'nochallenge', 'active2016']
    actions = [export_as_csv]

class CommutersurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
            {'fields': ['wr_day_month', 'name', 'email', 'employer', 'team', 'share', 'comments' ]}),
        ('Commute',
            {'fields': ['home_address', 'work_address']})
    ]
    list_display = ('id', 'wr_day_month', 'email', 'name', 'employer', 'team', 'home_address', 'work_address', 'carbon_change', 'calorie_change' )
    list_editable = ('employer', 'team')
    list_filter = ['wr_day_month', 'employer', 'team', 'share', 'volunteer']
    search_fields = ['name', 'email', 'employer__name', 'team__name']
    actions = [export_as_csv]

class LegAdmin(admin.ModelAdmin):
    list_display = ['id', 'direction', 'day', 'checkin', 'mode', 'duration', 'carbon', 'calories']
    list_filter = ('checkin__wr_day_month', 'mode__name')
    actions = [export_as_csv]

class MonthAdmin(admin.ModelAdmin):
    list_display = ['id', 'wr_day', 'open_checkin', 'close_checkin']
    list_editable = ['wr_day', 'open_checkin', 'close_checkin']
    actions = [export_as_csv]

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'nr_members']
    list_editable = ['name', 'parent', 'nr_members']
    actions = [export_as_csv]

class ModeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'met', 'carb', 'speed', 'green' ]
    list_editable = ['name', 'met', 'carb', 'speed', 'green']
    actions = [export_as_csv]

class SectorAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_editable = ['name']
    actions = [export_as_csv]

# add admin configuration for QOTM
class QOTMAdmin(admin.ModelAdmin):
    list_display = ['id', 'wr_day_month', 'value']
    list_editable = ['wr_day_month','value']
    actions = [export_as_csv]

admin.site.register(Commutersurvey, CommutersurveyAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Month, MonthAdmin)
admin.site.register(Leg, LegAdmin)
admin.site.register(Mode, ModeAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(QuestionOfTheMonth, QOTMAdmin)

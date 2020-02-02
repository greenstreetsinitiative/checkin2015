from django.contrib import admin

# Register your models here.

import csv
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Sum, Count

from django.forms import ModelForm


from survey.models import Commutersurvey, Employer, Leg, Month, Mode, Team, Sector, QuestionOfTheMonth, MonthlyQuestion, DonationOrganization

# disable deletion of records
admin.site.disable_action('delete_selected')

# Use for resaving surveys if saving logic is changed
def resave(modeladmin, request, queryset):
    for obj in queryset:
        obj.save()

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
            writer.writerow([encode(getattr(obj, field)) for field in field_names])
        except UnicodeEncodeError:
            print "Could not export data row."
    return response

def encode(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    else:
        return s

export_as_csv.short_description = "Export selected rows as csv file"

class EmployerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display_links = ['id']
    list_display = ['id', 'name', 'sector', 'nochallenge', 'active2018','active2019','active2020','nr_employees']
    list_editable = ['name', 'sector',  'nochallenge', 'active2018','active2019','active2020','nr_employees']
    actions = [export_as_csv]

class CommutersurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
            {'fields': ['wr_day_month', 'name', 'email', 'employer', 'team', 'share', 'comments' ]}),
        ('Commute',
            {'fields': ['home_address', 'work_address']})
    ]
    list_display = ('id', 'wr_day_month', 'email', 'name', 'employer', 'team', 'home_address', 'work_address', 'carbon_change', 'calorie_change', 'questionOne', 'questionTwo', 'questionThree', 'questionFour', 'questionFive' )
    list_filter = ['wr_day_month', 'share', 'volunteer']
    search_fields = ['name', 'email', 'employer__name', 'team__name']
    actions = [export_as_csv, resave]

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

class MonthlyQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wr_day_month', 'questionNumber', 'questionType', 'question', 'answer_1', 'answer_2', 'answer_3', 'answer_4', 'answer_5', 'answer_6', 'answer_7', 'answer_8', 'answer_9', 'answer_10', 'answer_11','answer_12' ,'answer_13','answer_14','answer_15']
    list_editable = ['wr_day_month', 'questionNumber', 'questionType', 'question', 'answer_1', 'answer_2', 'answer_3', 'answer_4', 'answer_5', 'answer_6', 'answer_7', 'answer_8', 'answer_9', 'answer_10', 'answer_11','answer_12' ,'answer_13','answer_14','answer_15']
    actions = [export_as_csv, 'delete_selected']

class DonationOrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'wr_day_month', 'organization_name','website']
    list_editable = ['wr_day_month','organization_name', 'website']
    actions = [export_as_csv]

admin.site.register(Commutersurvey, CommutersurveyAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Month, MonthAdmin)
admin.site.register(Leg, LegAdmin)
admin.site.register(Mode, ModeAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(QuestionOfTheMonth, QOTMAdmin)
admin.site.register(MonthlyQuestion, MonthlyQuestionAdmin)
admin.site.register(DonationOrganization, DonationOrganizationAdmin)

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    # Home
    url(r'^$', 'survey.views.index', name='home'),

    # Checkin page
    url(r'^checkin/$', 'survey.views.add_checkin', name='commuterform'),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^checkin/complete/$', TemplateView.as_view(template_name='survey/thanks.html'), name='complete'),

    # Leaderboard by year
    url(r'^leaderboard/((?P<year>[0-9]{4})/)?$',
        'leaderboard.views.latest_leaderboard', name="all"),


    url(r'^leaderboard/(?P<year>[0-9]{4})/all/subteams/$',
        'leaderboard.views.latest_leaderboard', name="subteams_all"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/all/all/subteams/(?P<parentid>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="subteams"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<sector>[\w\.-]*)/(?P<size>[\w\.-]*)/subteams/(?P<parentid>[\w\.-]*)/(?P<selected_month>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="subteams_months"),


    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<selected_month>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all_sizes_all_months"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<size>[\w\.-]*)/(?P<selected_month>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all_sizes_all_months"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<size>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all"),

    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<sector>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<sector>[\w\.-]*)/(?P<size>[\w\.-]*)/(?P<selected_month>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all"),
    url(r'^leaderboard/(?P<year>[0-9]{4})/(?P<sector>[\w\.-]*)/(?P<selected_month>[\w\.-]*)/$',
        'leaderboard.views.latest_leaderboard', name="all"),

    # individual company pages by year
    url(r'^companies/(?P<year>[0-9]{4})/$', 'leaderboard.views.company', name="allcompany"),
    url(r'^companies/(?P<year>[0-9]{4})/(?P<employerid>[\w\.-]*)/$', 'leaderboard.views.company', name="companies"),
    url(r'^companies/(?P<year>[0-9]{4})/(?P<employerid>[\w\.-]*)/(?P<teamid>[\w\.-]*)/$', 'leaderboard.views.company', name="teams"),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # Retail Partners
    url(r'^retail/$', include('retail.urls', namespace='retail')),

    # Employer Information Page
    url(r'^employers/(?P<secret_code>\w+)/(?P<year>[0-9]{4})/$', 'leaderboard.views.info', name="info"),

    # Render data for all months for Employer Information Page
    url(r'^render/(?P<employerid>[\w\.-]*)/(?P<shouldreplace>\w+)/$', 'leaderboard.views.render', name="render"),


) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

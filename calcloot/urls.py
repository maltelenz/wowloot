from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from wowloot import settings

import calcloot.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', calcloot.views.home, name = 'home'),
    url(r'^about/$', calcloot.views.about, name = 'about'),
    url(r'^person/a/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', calcloot.views.add_person, name = "add_person"),
    url(r'^person/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<personid>\d+)/$', calcloot.views.delete_person, name = "delete_person"),
    url(r'^person/f/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<personid>\d+)/$', calcloot.views.finish_person, name = "finish_person"),
    url(r'^person/u/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<personid>\d+)/$', calcloot.views.unfinish_person, name = "unfinish_person"),
    url(r'^currency/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', calcloot.views.change_currency, name = "change_currency"),
    url(r'^calculation/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', calcloot.views.calculation, name = "calculation"),
    url(r'^calculation/s/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', calcloot.views.calculation_share, name = "calculation_share"),
    url(r'^calculation/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', calcloot.views.calculation_delete, name = "calculation_delete"),
    url(r'^calculation/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<edit_expense_id>\d+)/$', calcloot.views.calculation, name = "expense_edit"),
    url(r'^expense/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/$', calcloot.views.expense_delete, name = "expense_delete"),
    url(r'^benefactor/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/(?P<personid>\d+)/$', calcloot.views.benefactor_delete, name = "benefactor_delete"),
    url(r'^benefactor/a/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/(?P<personid>\d+)/$', calcloot.views.benefactor_add, name = "benefactor_add"),
]

if settings.DEBUG:
    urlpatterns += [
                        url(r'^404/',
                            TemplateView.as_view(template_name='404.html')),
                        url(r'^500/',
                            TemplateView.as_view(template_name='500.html'))
                        ]

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('calcloot.views',
    # Examples:
    url(r'^$', 'home', name = 'home'),
    url(r'^person/a/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', 'add_person', name = "add_person"),
    url(r'^calculation/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', 'calculation', name = "calculation"),
    url(r'^calculation/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', 'calculation_delete', name = "calculation_delete"),
    url(r'^expense/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/$', 'expense_delete', name = "expense_delete"),
    url(r'^benefactor/d/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/(?P<personid>\d+)/$', 'benefactor_delete', name = "benefactor_delete"),
    url(r'^benefactor/a/(?P<calcid>\d+)/(?P<hashtag>\w+)/(?P<expenseid>\d+)/(?P<personid>\d+)/$', 'benefactor_add', name = "benefactor_add"),

)


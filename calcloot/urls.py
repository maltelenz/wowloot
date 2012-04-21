from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('calcloot.views',
    # Examples:
    url(r'^$', 'home', name = 'home'),
    url(r'^calculation/(?P<calcid>\d+)/(?P<hashtag>\w+)/$', 'calculation', name = "calculation"),

)


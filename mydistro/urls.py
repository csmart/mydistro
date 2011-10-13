from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mydistro.views.home', name='home'),
    # url(r'^mydistro/', include('mydistro.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


    # RACK VIEWS
    (r'^packages/$', 'rack.views.packages_index'),
    (r'^packages/(?P<package_id>[0-9a-fA-F]+)/$', 'rack.views.packages_detail'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

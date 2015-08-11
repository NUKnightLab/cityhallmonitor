from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'cityhallmonitor.views.search', name='search'),
    url(r'^about$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^facet$', 'cityhallmonitor.views.facet', name='facet'),
    url(r'^documents/(?P<id>[0-9]+)$', 
        'cityhallmonitor.views.documents', name='documents'),
]

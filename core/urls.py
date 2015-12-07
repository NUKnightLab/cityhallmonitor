from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'cityhallmonitor.views.search', name='search'),
    url(r'^process_query$', 'cityhallmonitor.views.process_query', name='process_query'),
    url(r'^about$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^subscriptions$', TemplateView.as_view(template_name='subscriptions.html'),
        name='subscriptions'),
    url(r'^faq$', TemplateView.as_view(template_name='faq.html'),
        name='faq'),
    url(r'^facet$', 'cityhallmonitor.views.facet', name='facet'),
    url(r'^documents/(?P<id>[0-9]+)$', 
        'cityhallmonitor.views.documents', name='documents'),   
    url(r'^send_notifications_link', 'cityhallmonitor.views.send_notifications_link', name='send_notifications_link'),
    url(r'^notifications$', 'cityhallmonitor.views.notifications', name='notifications'),
    url(r'^subscribe$', 'cityhallmonitor.views.subscribe', name='subscribe'),
    url(r'^activate$', 'cityhallmonitor.views.activate', name='activate'),
    url(r'^unsubscribe$', 'cityhallmonitor.views.unsubscribe', name='unsubscribe'),
]

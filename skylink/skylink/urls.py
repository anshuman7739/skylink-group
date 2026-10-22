from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from core.sitemaps import StaticViewSitemap

admin.site.site_header = 'Skylink Group of Companies Admin'
admin.site.site_title = 'Skylink Group Admin'
admin.site.index_title = 'Corporate Lead & Service Operations Portal'

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('staffing/', include('staffing.urls', namespace='staffing')),
    path('skill-academy/', include('academy.urls', namespace='academy')),
    path('maintenance/', include('maintenance.urls', namespace='maintenance')),
    path('dashboard/', include('submissions.urls', namespace='submissions')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'
    ), name='robots'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

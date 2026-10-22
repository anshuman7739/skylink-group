from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return [
            'core:home', 'core:about', 'core:contact',
            'core:privacy_policy', 'core:terms',
            'staffing:home', 'staffing:employer_enquiry', 'staffing:job_application',
            'academy:home', 'academy:course_admission',
            'maintenance:home', 'maintenance:service_request',
        ]

    def location(self, item):
        return reverse(item)

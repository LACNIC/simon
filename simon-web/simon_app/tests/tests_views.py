from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse


class ApiTestCase(TestCase):
    def get_section(self, url):
        c = Client()
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_objectives(self):
        return self.get_section(reverse("simon_app.views.objectives"))

    def test_participate(self):
            return self.get_section(reverse("simon_app.views.participate"))

    def test_reports(self):
        return self.get_section(reverse("simon_app.views.home"))

    def test_api(self):
        return self.get_section(reverse("simon_app.views.api"))

    def test_atlas(self):
        return self.get_section(reverse("simon_app.views.atlas"))

    def test_reports(self):
        return self.get_section(reverse("simon_app.views.reports"))

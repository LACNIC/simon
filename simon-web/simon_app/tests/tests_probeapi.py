from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse


class ViewTestCase(TestCase):

    OK = 200

    def get_section(self, url, status=OK):
        c = Client()
        response = c.get(url)
        self.assertEqual(response.status_code, status)

    def test_objectives(self):
        return self.get_section(reverse("simon_app.views.objectives"), self.OK)

    def test_participate(self):
            return self.get_section(reverse("simon_app.views.participate"), self.OK)

    def test_reports(self):
        return self.get_section(reverse("simon_app.views.home"), self.OK)

    def test_api(self):
        return self.get_section(reverse("simon_app.views.api"), self.OK)

    def test_atlas(self):
        return self.get_section(reverse("simon_app.views.atlas"), self.OK)

    def test_reports(self):
        return self.get_section(reverse("simon_app.views.reports"), self.OK)

    # def test_reports(self):
    #     return self.get_section(reverse("simon_app.views.charts"), self.OK)

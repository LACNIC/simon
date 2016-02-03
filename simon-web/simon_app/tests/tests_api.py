from tastypie.test import ResourceTestCase
from django.core.urlresolvers import reverse

# class ApiTestCase(ResourceTestCase):

    # def test_get_api_json(self, url):
    #     resp = self.api_client.get(url, format='json')
    #     self.assertValidJSONResponse(resp)

    # def test_autnum(self):
    #     url = reverse("simon_app.api_views.ases")
    #     print url
    #     return self.test_get_api_json(url)
    #
    # def test_latency(self):
    #     urls = reverse("simon_app.views.latency")
    #     print urls
    #     return self.test_get_api_json("/api/latency/BO/6")
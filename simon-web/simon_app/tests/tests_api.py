from django.test import TestCase
from django.test import Client

class ApiTestCase(TestCase):

     def test_api(self):
         c = Client()
         response = c.get('/')
         print response.status_code
         self.assertEqual(response.status_code, 404)
'''
Created on 30/08/2012

@author: agustinf
'''
from django.forms import forms
from django.forms.fields import ChoiceField
from simon_app.models import Country
from django.db.models import Q

class CountryForm(forms.Form):
    countries = Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).values('iso', 'printable_name')
    countries_list = []

    for country in countries:
        register = []
        register.append(country['iso'])
        register.append(country['printable_name'])
        countries_list.append(register)
    countries = ChoiceField(countries_list, label='Please select your country')
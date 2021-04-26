# -*- coding: utf-8 -*-

"""
    File that defines the non-persistent classes
"""

from __future__ import division
from django import forms
from datetime import tzinfo, timedelta
from simon_app.models.models import *
import datetime


class MyImageModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s Bytes" % (obj.size)


class MyCountryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.printable_name)


class CountryDropdownForm(forms.Form):
    default_country = None
    country = MyCountryModelChoiceField(
        queryset=Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name'),
        widget=forms.Select(), label='País que desea inspeccionar la latencia',
        empty_label=default_country)


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Archivo con logs de traceroute", required=False)


class YearField(forms.ChoiceField):
    year = range(2009, datetime.datetime.now().year + 1)


class ASForm(forms.Form):
    ases = AS.objects.all()[:100]  # TODO cambiar para que abarque los regionales
    as_dropdown = forms.ModelChoiceField(queryset=ases,
                                         widget=forms.Select(attrs={'class': 'form-control'}),
                                         label="Sistema autónomo")


class ReportForm(forms.Form):
    """
        Form used for country-level reports.
    """
    # default_country = None
    empty_label = "Toda la región"

    region_objects_filter = Region.objects.filter(Q(name="South America") | Q(name="Central America") | Q(name="Caribbean"))
    countries_from_region = Country.objects.get_countries_from_region()
    countries = Country.objects.get_lacnic_countries()
    country1 = MyCountryModelChoiceField(queryset=countries.order_by('printable_name'),
                                         widget=forms.Select(attrs={'class': 'form-control'}),
                                         label="País de origen de las mediciones",
                                         empty_label=empty_label
                                         )

    country2 = MyCountryModelChoiceField(queryset=countries.order_by('printable_name'),
                                         widget=forms.Select(attrs={'class': 'form-control'}),
                                         label="País de destino de las mediciones",
                                         required=False,
                                         empty_label=empty_label
                                         )

    bidirectional = forms.NullBooleanField(
        required=False,
        initial=True,
        label="Bidireccional",
        help_text="Desmarcar esta opción si se desea filtrar mediciones en el sentido país origen --> país destino únicamente"
    )

    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}),
        label="Fecha desde"
    )

    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}),
        label="Fecha hasta",
        required=False
    )

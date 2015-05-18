__author__ = 'agustin'
from django import forms

class FeedbackForm(forms.Form):
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'style':'background-color:#F1EFEE'}))
    remitente = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'style':'background-color:#F1EFEE'}))
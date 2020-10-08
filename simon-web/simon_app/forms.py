
from django import forms


class FeedbackForm(forms.Form):
    mensaje = forms.CharField(
        help_text="",
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'style': 'margin-bottom: .5em',
                'placeholder': "Tu mensaje..."
            }
        ))
    remitente = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'style': 'margin-bottom: .5em',
                'placeholder': "Remitente"
            }
        ))

from django import forms

class LogUploadForm(forms.Form):
    file = forms.FileField(label='Plik .adi', widget=forms.FileInput())

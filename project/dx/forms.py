from django import forms

class LogUploadForm(forms.Form):
    file = forms.FileField(label='Plik', widget=forms.FileInput(attrs={'class': "form-control"}))

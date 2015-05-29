from django import forms

class LogUploadForm(forms.Form):
    file = forms.FileField(label='Plik', widget=forms.FileInput(attrs={'class': "form-control"}))

class ProfileForm(forms.Form):
    callsign = forms.CharField(label='Your Callsign', widget=forms.TextInput(attrs={'id': 'callsign', 'class': "form-control"}))
    locator = forms.CharField(label='Locator gridsquare', widget=forms.TextInput(attrs={'id': 'locator', 'class': "form-control"}))

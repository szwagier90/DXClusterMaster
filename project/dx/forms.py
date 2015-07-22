# -*- coding: utf-8 -*-

from django import forms

from django.contrib.auth.models import User

from models import Band, Operator, Filter

class LogUploadForm(forms.Form):
    file = forms.FileField(label='Plik .adi', widget=forms.FileInput())

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(label=u'Imię', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=u'Nazwisko', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u'E-mail', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class OperatorEditForm(forms.ModelForm):
    callsign = forms.CharField(label=u'Znak wywoławczy', widget=forms.TextInput(attrs={'class': 'form-control'}))
    locator = forms.CharField(label=u'Lokator', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['callsign', 'locator']

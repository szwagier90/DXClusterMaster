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

class FilterEditForm(forms.ModelForm):
    bands = forms.ModelMultipleChoiceField(
                queryset=Band.objects.all().order_by('start_frequency'),
                label=u'Pasma',
                widget=forms.SelectMultiple(attrs={'class': 'form-control'})
            )
    show_qsl_confirmed = forms.BooleanField(label=u'QSL', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    show_eqsl_confirmed = forms.BooleanField(label=u'eQSL', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    show_lotw_confirmed = forms.BooleanField(label=u'LOTW', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Filter
        fields = ['bands', 'show_qsl_confirmed', 'show_eqsl_confirmed', 'show_lotw_confirmed']

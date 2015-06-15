from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import View

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from models import Spot, Operator, QSO
from forms import LogUploadForm, ProfileForm

from tempfile import NamedTemporaryFile

from AdiLogParser import AdiLogParser

from drafts import colors

class IndexView(TemplateView):
    template_name = 'dx/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['ten_recent_spots'] = Spot.objects.order_by('-id')[:10]
        return context

class RegisterView(FormView):
    template_name = 'dx/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = form.save()
        operator = Operator(user=user)
        operator.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return super(RegisterView, self).form_valid(form)

class ProfileView(DetailView):
    model = User

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class ProfileEdit(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class OperatorView(DetailView):
    model = Operator

    def get_object(self, queryset=None):
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class OperatorEdit(UpdateView):
    model = Operator
    fields = ['callsign',  'locator']
    success_url = reverse_lazy('operator')

    def get_object(self, queryset=None):
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class LogUploadView(FormView):
    template_name = 'dx/upload.html'
    form_class = LogUploadForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        self.handle_uploaded_file(self.request.FILES['file'])
        return super(LogUploadView, self).form_valid(form)

    def handle_uploaded_file(self, f):
        with NamedTemporaryFile() as temp_file:
            for chunk in f.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            adi = AdiLogParser(temp_file.name)

        operator = Operator.objects.get(user__username=self.request.user)
        keys = set()
        for record in adi.parsed_records:
            for key in record.keys():
                keys.add(key)

        for record in adi.parsed_records:
            qso = QSO()
            qso.operator = operator

            qso.call = self.read_key_from_record('CALL', record)
            qso.date = self.read_key_from_record('DATE', record)
            qso.cqz = self.read_key_from_record('CQZ', record)
            qso.band = self.read_key_from_record('BAND', record)
            qso.ituz = self.read_key_from_record('ITUZ', record)
            qso.dxcc = self.read_key_from_record('DXCC', record)
            qso.frequency = self.read_key_from_record('FREQ', record)
            qso.locator = self.read_key_from_record('GRIDSQUARE', record)
            qso.mode = self.read_key_from_record('MODE', record)
            qso.rst_sent = self.read_key_from_record('RST_SENT', record)
            qso.rst_received = self.read_key_from_record('RST_RCVD', record)
            qso.qsl_confirmed = self.read_key_from_record('QSL_RCVD', record)
            qso.eqsl_confirmed = self.read_key_from_record('eQSL_QSL_RCVD', record)
            qso.lotw_confirmed = self.read_key_from_record('LOTW_QSL_RCVD', record)
            qso.save()

    def read_key_from_record(self, key, record):
        exception_values = {
            'CALL': None,
            'DATE': None,
            'CQZ': None,
            'BAND': None,
            'ITUZ': None,
            'DXCC': None,
            'FREQ': None,
            'GRIDSQUARE': None,
            'MODE': None,
            'RST_SENT': None,
            'RST_RCVD': None,
            'QSL_RCVD': False,
            'eQSL_QSL_RCVD': False,
            'LOTW_QSL_RCVD': False,
        }

        try:
            return record[key]
        except KeyError:
            return exception_values[key]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.core import serializers
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

import time
import json

from .models import Person, RequestStore
from .decorators import not_record_request
from .forms import PersonForm


def home_page(request):
    context = {}
    person = Person.objects.first()
    context['person'] = person
    return render(request, 'home.html', context)


@not_record_request
def request_view(request):
    if request.user.is_authenticated():
        RequestStore.objects.filter(new_request=1).update(new_request=0)
    return render(request, 'request.html')


@not_record_request
def request_ajax(request):
    if request.is_ajax():
        new_request = RequestStore.objects.filter(new_request=1).count()
        request_list = RequestStore.objects.all()[:10]
        list = serializers.serialize("json", request_list) 
        r = [{'list': list, 'num': new_request}]
        data = json.dumps((new_request, list))
        print data
        return HttpResponse(data, content_type="application/json")

    return None


@login_required
@not_record_request
def form_page(request):
    if request.POST:
        form = PersonForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            bio = form.cleaned_data.get('bio')
            email = form.cleaned_data.get('email')
            jabber = form.cleaned_data.get('jabber')
            skype_id = form.cleaned_data.get('skype_id')
            other = form.cleaned_data.get('other')

            person = Person(name=name,
                            surname=surname,
                            date_of_birth=date_of_birth,
                            bio=bio,
                            email=email,
                            jabber=jabber,
                            skype_id=skype_id,
                            other=other)
            person.save()
            if request.is_ajax():
                if getattr(settings, 'DEBUG', False):
                    time.sleep(3)
                msg = 'Contact was added'
                return HttpResponse(json.dumps({'msg': msg}))
            else:
                return redirect('hello:success')
        else:
            if request.is_ajax():
                if getattr(settings, 'DEBUG', False):
                    time.sleep(2)
                errors = json.dumps(form.errors)
                return HttpResponse(errors)
    else:
        form = PersonForm()

    return render(request, 'form.html', {'form': form})

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse

import json

from .models import Person, RequestStore


def home_page(request):
    context = {}
    person = Person.objects.first()
    context['person'] = person
    return render(request, 'home.html', context)


def request_view(request):
    return render(request, 'request.html')


def request_ajax(request):
    if request.is_ajax():
        request_list = RequestStore.objects.all()
        r = serializers.serialize("json", request_list)
        data = json.dumps(r)

        return HttpResponse(data, content_type="application/json")

    return None

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse

import json

from .models import Person, RequestStore
from .decorators import not_record_request


def home_page(request):
    context = {}
    person = Person.objects.first()
    context['person'] = person
    return render(request, 'home.html', context)


@not_record_request
def request_view(request):
    if request.user.username == 'admin':
        RequestStore.objects.filter(new_request=1).update(new_request=0)
    return render(request, 'request.html')


@not_record_request
def request_ajax(request):
    if request.is_ajax():
        request_list = RequestStore.objects.all()
        r = serializers.serialize("json", request_list)
        data = json.dumps(r)

        return HttpResponse(data, content_type="application/json")

    return None

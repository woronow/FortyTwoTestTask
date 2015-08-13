# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from apps.hello.models import RequestStore


class RequestMiddle(object):
    def process_request(self, request):
        if request.get_full_path() == '/requests/':
            if request.user.username == 'admin':
                RequestStore.objects.filter(new_request=1)\
                                    .update(new_request=0)
        elif request.get_full_path() != '/request_ajax/':
            req = RequestStore()
            req.path = request.path
            req.method = request.method

            if request.user.is_authenticated():
                req.user = request.user

            req.save()

        return None

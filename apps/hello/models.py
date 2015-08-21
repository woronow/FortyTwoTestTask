# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Person(models.Model):
    name = models.CharField('name', max_length=250)
    surname = models.CharField('surname', max_length=250)
    date_of_birth = models.DateField('date of birth')
    bio = models.TextField('bio', blank=True)
    email = models.EmailField('email')
    jabber = models.EmailField('jabber', blank=True)
    skype_id = models.CharField('skype id',
                                blank=True,
                                max_length=250)
    other = models.TextField('other contact', blank=True)
    image = models.ImageField('photo',
                              blank=True,
                              null=True,
                              upload_to='photo/',
                              height_field='height',
                              width_field='width')
    height = models.PositiveIntegerField(default=1, blank=True)
    width = models.PositiveIntegerField(default=1, blank=True)

    def gauge_height(self):
        width = 200
        ratio = float(self.height)/float(self.width)
        height = width*ratio
        size_photo = {'w': width, 'h': height}
        return size_photo

    def __unicode__(self):
        return '%s %s' % (self.surname, self.name)


class RequestStore(models.Model):
    path = models.CharField(max_length=250)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True,
                             null=True)
    date = models.DateTimeField(auto_now_add=True)
    new_request = models.PositiveIntegerField(default=1)

    def __unicode__(self):
        return "%s - %s" % (self.path, self.method)

    class Meta:
        ordering = ["-date"]


class NoteModel(models.Model):
    ACTION_TYPE = (
        (0, 'created'),
        (1, 'changed'),
        (2, 'deleted')
    )
    model = models.CharField('model', max_length=50)
    inst = models.CharField('instance', max_length=250)
    action_type = models.PositiveIntegerField('action type',
                                              max_length=1,
                                              choices=ACTION_TYPE)

    def __unicode__(self):
        return "%s  %s: %s " % (self.model,
                                self.get_action_type_display(),
                                self.inst)


@receiver([post_save, post_delete])
def models_handler(sender, **kwargs):
    model = sender.__name__
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    update_fields = kwargs.get('update_fields')
    action_type = 2

    if model != 'NoteModel':
        if model != 'LogEntry':
            if created is not None:
                action_type = 0
            elif update_fields is not None:
                action_type = 1
            note = NoteModel(model=model,
                             inst=instance,
                             action_type=action_type)
            note.save()

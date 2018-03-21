# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import config
import uuid
# Create your models here.

def upload_to(instance, filename):
    terms = filename.split('.')
    terms[0] = str(uuid.uuid1())
    filename = '.'.join(terms)
    return '/'.join([config.IMAGE_ROOT, filename])

class Image(models.Model):
    openid = models.CharField(max_length=128, db_index=True, default='')
    title = models.CharField(max_length=200)
    fpath =  models.FileField(upload_to=upload_to)
    ftime = models.CharField(max_length=30)

    def todict(self):
        return {'title':self.title, 'fpath':config.ROOT_URL + self.fpath.url, 'ftime':self.ftime}
    

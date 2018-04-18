# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import config
import uuid
# Create your models here.

class User(models.Model):
    openid = models.CharField(max_length=128, primary_key=True)
    avatarUrl = models.CharField(max_length=200)
    nickName = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)

def upload_to(instance, filename):
    terms = filename.split('.')
    terms[0] = str(uuid.uuid1())
    filename = '.'.join(terms)
    return '/'.join([config.IMAGE_ROOT, filename])

class Image(models.Model):
    openid = models.CharField(max_length=128)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1024)
    fpath =  models.FileField(upload_to=upload_to)
    album_id = models.CharField(max_length=128, db_index=True)
    index = models.IntegerField(default=0) 

    class Meta:
        index_together = ('openid', 'album_id', 'index')

    def todict(self):
        filename = str(self.fpath.url).split("/")[-1]
        return {'title':self.title, 'content':self.content, 'fpath':config.DATA_URL + filename, 'album_id':self.album_id, 'index':self.index}

class Reward(models.Model):
    openid = models.CharField(max_length=128)
    album_id= models.CharField(max_length=128, default="-1")
    ropenid = models.CharField(max_length=128)
    rtime = models.CharField(max_length=32)
    amount = models.FloatField()

    class Meta:
        index_together = ('openid', 'album_id')

    def todict(self):
        return {"album_id":self.album_id, "amount":self.amount, "rtime":self.rtime}

    

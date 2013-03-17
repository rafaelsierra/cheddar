# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from feeds.models import Site

# TODO: Make User.email unique

class Folder(BaseModel):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=32)
    

class UserSite(BaseModel):
    user = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    folder = models.ForeignKey(Folder, null=True, blank=True)
    
    class Meta:
        unique_together = (('user', 'site'),)
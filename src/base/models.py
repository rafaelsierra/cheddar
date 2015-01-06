# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet


class BaseModelQueryset(QuerySet):
    def newest(self):
        try:
            return self.order_by('-created_at')[0]
        except IndexError:
            return None
        
    def actives(self):
        '''Retorna apenas os objetos ativos'''
        return self.filter(is_active=True)


class BaseModelManager(models.Manager):
    def newest(self):
        return self.get_queryset().newest()
    
    def get_queryset(self):
        return BaseModelQueryset(self.model)

    def actives(self):
        return self.get_queryset().actives()
        

class BaseModel(models.Model):
    '''Classe abstrata pra armazenar data de criação e atualização do objeto'''
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    objects = BaseModelManager()
    
    class Meta:
        abstract = True
        

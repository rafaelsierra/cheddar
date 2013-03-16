# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings

def start_feed_update(sender, instance, created, **kwargs):
    elapsed_time = timezone.now() - instance.updated_at 
    if created or elapsed_time > settings.MAX_UPDATE_WAIT:
        instance.update_feed()

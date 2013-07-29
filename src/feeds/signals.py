# -*- coding: utf-8 -*-
import logging
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('feeds.signals')

def start_feed_update(sender, instance, created, **kwargs):
    elapsed_time = timezone.now() - instance.updated_at 
    if created or elapsed_time > settings.MAX_UPDATE_WAIT:
        try:
            instance.update_feed()
        except Exception, e:
            logger.exception('Failed starting feed update')
            

# -*- coding: utf-8 -*-

def update_site_data(sender, instance, **kwargs):
    # TODO: Check if is really needed do the update
    instance.update_data()

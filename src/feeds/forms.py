# -*- coding: utf-8 -*-
import listparser
from django import forms
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

class ImportSubscriptionForm(forms.Form):
    xml_file = forms.FileField(label=_('File'), help_text=_('Your subscriptions.xml file'))
    
    def clean_xml_file(self):
        xml_file = self.cleaned_data['xml_file']
        result = listparser.parse(xml_file)
        
        if result['bozo'] == 1:
            raise ValidationError(result['bozo_exception'])
        
        self.result = result
        return xml_file

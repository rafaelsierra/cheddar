# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    '''Extends the default user creation form to add email as a required field'''
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError(_("This field is required."))
        return email
    
    class Meta:
        model = User
        fields = ('username', 'email')
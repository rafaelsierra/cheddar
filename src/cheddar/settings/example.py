# -*- coding: utf-8 -*-
from .default import *

# Here you can set DATABASES, MEDIA_ROOT, STATIC_ROOT, etc

# Don't forget to add the following in your file
import djcelery
djcelery.setup_loader()

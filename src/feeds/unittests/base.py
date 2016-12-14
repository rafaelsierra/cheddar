from rest_framework.test import APITestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

class APICeleryTestCase(APITestCase):
    def setUp(self, *args, **kwargs):
        super(APICeleryTestCase, self).setUp(*args, **kwargs)

# x_auth/apps.py
from django.apps import AppConfig

import os

class XAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'x_auth'

    def ready(self):
        # نتحقق من أننا لا نشغل المجدول مرتين أو في عملية الـ Reloader
        if os.environ.get('RUN_MAIN') == 'true':
            from . import operator
            operator.start()
# This is an example of which settings which resides in local_settings.py
# Copy this to local_settings.py and make your changes there.

"""
This is an extension of settings.py that contains sensitive information,
or local settings which override project defaults. This lets basic settings
like translation be committed to version control and shared, while stuff like
database setup is placed here.
"""

import sys

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd6w(v!yjnk2osjnz+xl*9tdlt##_^()z*u8pwn9^uee4442#*o'

ALLOWED_HOSTS = [
    '*',
]

INTERNAL_IPS = ['localhost', '127.0.0.1']

MEDIA_ROOT = 'media-root/'

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'buk',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
    },
}

"""Uncomment these lines to be able to import from legacy database
if 'test' not in sys.argv:
    DATABASES['legacy'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'buk',
        'USER': 'buk',
        'PASSWORD': 'buk',
        'HOST': '',
    }
"""

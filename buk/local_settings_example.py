# This is an example of which settings which resides in local_settings.py
# Copy this to local_settings.py and make your changes there.

"""
This is an extension of settings.py that contains sensitive information,
or local settings which override project defaults. This lets basic settings
like translation be committed to version control and shared, while stuff like
database setup is placed here.
"""

# SECURITY WARNING: keep the secret key used in production secret!
# You can generate your own key here:
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = 'd6w(v!yjnk2osjnz+xl*9tdlt##_^()z*u8pwn9^uee4442#*o'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

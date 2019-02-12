import random
import string


def management_form_to_post(management_form):
    keys = ['TOTAL_FORMS', 'INITIAL_FORMS', 'MIN_NUM_FORMS', 'MAX_NUM_FORMS']
    return {'{}-{}'.format(management_form.prefix, key): management_form[key].value() for key in keys}


def management_form_data(total=1, initial=1, min_num=0, max_num=20):
    return {
        'TOTAL_FORMS': total,
        'INITIAL_FORMS': initial,
        'MIN_NUM_FORMS': min_num,
        'MAX_NUM_FORMS': max_num,
    }


def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def permission_to_perm(permission):
    """Find the <app_label>.<codename> string for a permission object"""
    return '.'.join([permission.content_type.app_label, permission.codename])

def form_to_post(form):
    """Extract POST data from a form"""
    post = {}

    for field in form.fields:
        name = form[field].html_name
        value = form[field].value()
        if not value and value != 0:
            value = ""

        post[name] = value

    return post


def formset_to_post(formset):
    """
    Extract POST data that will recreate the formset.
    """
    post = {}
    forms = [formset.management_form, *formset.forms]

    for form in forms:
        post.update(form_to_post(form))

    return post

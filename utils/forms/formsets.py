def formset_to_post(formset):
    """
    Extract POST data that will recreate the formset.
    """
    post = {}
    forms = [formset.management_form, *formset.forms]

    for form in forms:
        for field in form.fields:
            name = form[field].html_name
            value = form[field].value()

            post[name] = value

    return post

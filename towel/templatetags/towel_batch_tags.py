from django import template


register = template.Library()


@register.simple_tag
def batch_checkbox(form, id):
    """
    Checkbox which allows selecting objects for batch processing::

        {% for object in object_list %}
            {% batch_checkbox batch_form object.id %}
            {{ object }} etc...
        {% endfor %}
    """

    if not form or not hasattr(form, 'ids'):
        return u''

    cb = u'<input type="checkbox" name="batch_%s" value="%s" class="batch" %s/>'

    if id in form.ids:
        return cb % (id, id, 'checked="checked" ')

    return cb % (id, id, '')

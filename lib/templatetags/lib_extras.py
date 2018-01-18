from django import template
from django.contrib.contenttypes.models import ContentType


register = template.Library()

@register.filter
def content_type_pk(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj).pk

@register.filter
def content_type(obj):
    if not obj:
        return False
    return str(ContentType.objects.get_for_model(obj))

@register.filter
def img_class(img, size):
    height = img.height
    width = img.width

    if height < width:
        html = "circular-landscape"
    elif height > width:
        html = "circular-portrait"
    else:
        html = "circular-square"

    if size == "small":
        html += "-sm"

    return html

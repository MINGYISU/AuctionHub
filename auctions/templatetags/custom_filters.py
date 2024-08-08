from django import template
from auctions.models import Listing, Bid

register = template.Library()

@register.filter
def is_instance(value, class_name):
    if class_name == "Listing":
        return isinstance(value, Listing)
    elif class_name == "Bid":
        return isinstance(value, Bid)
    return False

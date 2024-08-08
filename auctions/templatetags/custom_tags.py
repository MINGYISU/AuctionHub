from django import template
from auctions.models import Listing, Bid

register = template.Library()

@register.simple_tag
def get_bids_all():
    return Bid.objects.all()

@register.simple_tag
def get_bids_filter(listing):
    return Bid.objects.filter(belonging=listing)

@register.simple_tag
def get_bids_highest(listing):
    highest = get_bids_filter(listing).last()
    return highest.curBid if highest else None


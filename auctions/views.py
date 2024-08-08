from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import Http404
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    # No need to provide a user parameter because user is already included in "request"
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(), 
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        # Check if there is a user that matches the username and password
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            # The user exists, login the user
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        # remember the url that was trying to access before
        next_url = request.GET.get('next', '')
        return render(request, "auctions/login.html", {
            "next": next_url
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    user = request.user
    if request.method == "POST":
        # extract the info received
        title = request.POST["title"]
        description = request.POST["description"]
        startBid = request.POST["startBid"]

        # Insert a new Listing object into the database
        listing = Listing(seller=user, title=title, description=description, startBid=startBid)
        listing.save()

        # redirect to the detailed page of the created listing
        return HttpResponseRedirect(reverse("display", args=[listing.id]))
    else:
        # return the create page
        return render(request, "auctions/create.html")

def get_cur_bid(listing):
    # gets the current bid of the listing
    bids = Bid.objects.filter(belonging=listing)
    return bids.last().curBid if bids else listing.startBid


def display_render(request, listing, filename, message=None):
    # renders the display or placebid page
    parameters = {
        "listing": listing, 
        "price": get_cur_bid(listing), 
        "bidders": Bid.objects.filter(belonging=listing)[::-1], 
        "exist": Watchlist.objects.filter(creator=request.user, belonging=listing).exists(), 
        "owner": request.user.id == listing.seller.id, 
        "comments": Comment.objects.filter(target=listing).all()[::-1]
    }
    
    # if a message is provided, display the message
    if message:
        parameters["message"] = message
    return render(request, f"auctions/{filename}.html", parameters)


def display(request, identity):
    if request.method == "GET":
        listing = get_object_or_404(Listing, id=identity)
        # if the listing is not closed
        if not listing.finished:
            return display_render(request, listing, "display")
        # if the listing is closed
        else:
            # if there is no bidder, then return a None as winner
            winner = None
            # get the list of all the bids
            lst = Bid.objects.filter(belonging=listing)
            # if there is at least one bid
            if lst:
                # the latest bidder will be the winner
                winner = lst.last().bidder.username

            return render(request, "auctions/closed.html", {
                "listing": listing, 
                "price": get_cur_bid(listing), 
                "winner": winner
            })
        

@login_required
def place_bid(request, identity):
    user = request.user
    listing = get_object_or_404(Listing, id=identity)

    # if bidding on a finished auction listing, raise an error
    if listing.finished:
        raise Http404("Cannot bid on a closed listing!")

    if user.id == listing.seller.id:
        raise Http404("Seller cannot place a bid!")
    
    if request.method == "POST":
        yourbid = request.POST["yourbid"]
        curbid = get_cur_bid(listing)

        # Later bid must be larger than the current bid
        if not (Decimal(yourbid) > Decimal(curbid)):
            message = "Your bid must be larger than the current bid!"
            return display_render(request, listing, "placebid", message=message)
        
        # insert a new bid into the database
        newbid = Bid(bidder=user, belonging=listing, curBid=yourbid)
        newbid.save()

        # redirect to the detailed page of the listing bidding on
        return HttpResponseRedirect(reverse('display', args=[identity]))
    else:
        return display_render(request, listing, "placebid")

@login_required
def change_wl(request, identity):
    # either add or remove a listing from the user's watchlist based on the existence of the listing in the watchlist
    user = request.user
    listing = get_object_or_404(Listing, id=identity)
    is_in = Watchlist.objects.filter(creator=user, belonging=listing).exists()

    # the listing is not in the watchlist, add it
    if not is_in:
        new_wl = Watchlist(belonging=listing, creator=user)
        new_wl.save()
    # the listing is in the watchlist, remove it
    else:
        del_wl = Watchlist.objects.get(belonging=listing, creator=user)
        del_wl.delete()
    
    # redirect to the detailed page of the listing
    return HttpResponseRedirect(reverse('display', args=[identity]))


@login_required
def show_watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(creator=user)
    # create a list for the listings in the watchlist
    listings = [item.belonging for item in watchlist]

    return render(request, "auctions/index.html", {
        "listings": listings, 
        "watchfor": user.username
    })

@login_required
def close(request, identity):
    user = request.user
    listing = get_object_or_404(Listing, id=identity)
    seller = listing.seller

    # if the user is not the seller, raise an error
    if user.id != seller.id:
        raise Http404("Error! You cannot close this page!")

    # change the state to True
    listing.finished = True
    listing.save()

    # redirect to the detailed page of the listing
    return HttpResponseRedirect(reverse('display', args=[identity]))

@login_required
def write_comment(request, identity):
    writer = request.user
    listing = get_object_or_404(Listing, id=identity)

    if listing.finished:
        raise Http404("Listing closed! Cannot add comments! ")

    if request.method == "POST":
        # create a new comment instance
        content = request.POST["content"]
        new_comm = Comment(writer=writer, target=listing, content=content)
        new_comm.save()

        return HttpResponseRedirect(reverse('display', args=[identity]))
    else:
        return render(request, "auctions/comment.html", {
            "listing": listing, 
            "comments": Comment.objects.filter(target=listing).all()[::-1], 
            "owner": request.user.id == listing.seller.id, 
            "price": get_cur_bid(listing)
        })

@login_required
def sell_list(request):
    user = request.user
    sellings = Listing.objects.filter(seller=user)
    lst = [item for item in sellings]
    return render(request, "auctions/index.html", {
        "listings": lst, 
        "createdby": user.username
    })

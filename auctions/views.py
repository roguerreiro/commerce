
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from datetime import datetime


from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    listings = Listing.objects.filter(active=True)
    full_listings = []
    for listing in listings:
        full_listings += [Bid.objects.get(auction=listing)]
    return render(request, "auctions/index.html", {
        "listings": full_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
def new_listing(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        starterbid = request.POST.get('starterbid')
        category = request.POST.get('category')
        image = request.POST.get('image')
        if title == '' or description == "":
            message = "Please fill in all fields correctly."
            return render(request, "auctions/new.html", {
                "message": message
            })
        user = request.user
        cur_date = datetime.now().date()
        cur_time = datetime.now().time()
        listing = Listing(user=user, item=title, description=description, category=category, date=cur_date, time=cur_time, image=image)
        listing.save()
        bid = Bid(bidder=user, auction=listing, bid=starterbid, starterbid=starterbid)
        bid.save()
        url = "/listing/" + str(Bid.objects.get(auction=listing).auction.id)
        return redirect(url)
    else:
        return render(request, "auctions/new.html")

def view_listing(request, key):
    listing = Listing.objects.get(id=key)
    full_listing = Bid.objects.get(auction=listing)

    if request.method == "POST":
        # Remove from watchlist
        if request.POST.get('remove'):
            watchlist = Watchlist.objects.filter(user=request.user, auction=listing).delete()
            request.method = "GET"

        # Add to Watchlist
        elif request.POST.get('add'):
            add = Watchlist(user=request.user, auction=listing)
            add.save()
            request.method = "GET"

        # Make a comment
        elif request.POST.get('comment'):
            comment = request.POST.get('comment')
            newcomment = Comment(commenter=request.user, auction=listing, comment=comment)
            newcomment.save()

        # Close auction
        elif request.POST.get('close'):
            Listing.objects.filter(id=key).update(active=False)

        # Place new bid
        else:
            newbid = float(request.POST.get('bid'))
            previousbid = float(full_listing.bid)
            starterbid = float(full_listing.starterbid)
            request.method = "GET"
            if newbid < starterbid:
                message = 'New bid must be as high as the starter bid.'
                return render(request, "auctions/listing.html", {
                    "listing": full_listing,
                    "message": message
                })
            elif newbid <= previousbid:
                message = "New bid must be higher than the previous bid."
                return render(request, "auctions/listing.html", {
                    "listing": full_listing,
                    "message": message
                })
            Bid.objects.filter(auction=listing).update(bid=newbid)
            Bid.objects.filter(auction=listing).update(bidder=request.user)
    full_listing = Bid.objects.get(auction=listing)
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user, auction=listing)
    else:
        watchlist = None
    comments = Comment.objects.filter(auction=listing)
    return render(request, "auctions/listing.html", {
        "listing": full_listing,
        "watchlist": watchlist,
        "comments": comments
    })

def categories(request, categ):
    categs = ('Books', 'Beauty and makeup', 'Clothing', 'Electronics', 'Home', 'Toys')
    if categ == 'all':
        return render(request, "auctions/categorylist.html", {
            "categories": categs
        })
    elif categ in categs:
        listings = Listing.objects.filter(category=categ)
        full_listings = []
        for listing in listings:
            full_listings += [Bid.objects.get(auction=listing)]
        return render(request, "auctions/category.html", {
            "category": categ,
            "listings": full_listings
        })
    else:
        message = "It looks like the category you are looking for doesn't exist!"
        return render(request, "auctions/category.html", {
            "message": message
        })

@login_required
def watchlist(request):
    listings = Watchlist.objects.filter(user=request.user)
    full_listings = []
    for listing in listings:
        full_listings += [Bid.objects.get(auction=listing.auction)]
    return render(request, "auctions/watchlist.html", {
        "listings": full_listings
    })

@login_required
def mylistings(request):
    listings = Listing.objects.filter(user=request.user)
    full_listings = []
    for listing in listings:
        full_listings += [Bid.objects.get(auction=listing)]
    return render(request, "auctions/mylistings.html", {
        "listings": full_listings
    })

@login_required
def won(request):
    listings = Listing.objects.filter(active=False)
    full_listings = []
    for listing in listings:
        if Bid.objects.filter(bidder=request.user, auction=listing):
            full_listings += [Bid.objects.get(auction=listing)]
    return render(request, "auctions/won.html", {
        "listings": full_listings
    })

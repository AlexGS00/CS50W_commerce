from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from datetime import date
from .models import Listing, User, Comment

from .models import User

categories = [
    ('Gym equipment', "Gym equipment"),
    ("Supliments", "Supliments"),
    ("Clothes", "Clothes"),
    ("Accessories", "Accessories")
]

class Add_Bid(forms.Form):
    title = forms.CharField(label='Listing title', widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'Title'}))
    description = forms.CharField(label='Listing description', widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'Description'}))
    bid = forms.IntegerField(label='Starting bid',widget=forms.NumberInput(attrs={'autocomplete':'off', 'placeholder':'Starting bid'}))
    link = forms.URLField(label="Photo link", widget=forms.URLInput(attrs={'autocomplete':'off', 'placeholder':'URL of photo'}), required=False)
    category = forms.CharField(label="Category", widget=forms.Select(choices=categories))

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def create_listing(request):
    if request.method == "GET":
        form = Add_Bid()
        return render(request, "auctions/create.html", {"form": form})
    else:
        form = Add_Bid(request.POST)
        if form.is_valid():
            #get the data for the listing
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["bid"]
            url = form.cleaned_data["link"]
            category = form.cleaned_data["category"]
            today = date.today()
            today_text = today.strftime("%d %B %Y")
            #create the new listing
            listing = Listing(title=title, description=description, bid=bid, photo_url=url, category=category, creation_date=today_text)
            listing.save()
            # Add the newly created listing to the listings field of the current user
            request.user.listings.add(listing)
            
            return HttpResponseRedirect(reverse("index"))
        new_form = Add_Bid()
        return render(request, "auctions/create.html", {"message": "The title, description, and bid sections are mandatory", "form": new_form})

            
def view_listing(request, listing_id):
    if request.method == "POST":
        text = request.POST["comment"]
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        today = date.today()
        today_text = today.strftime("%d %B %Y")
        comment = Comment(text=text,listing=listing,user=user,creation_date=today_text)
        comment.save()
        return HttpResponseRedirect(reverse(view_listing, args=(listing_id,)))
    else:
        listing = Listing.objects.get(pk=listing_id)
        comments = listing.comments.all()
        user_watchlist = request.user.watchlist
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments
        })
    
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse(view_listing, args=(listing_id,)))

def view_watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "watchlist" : watchlist
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

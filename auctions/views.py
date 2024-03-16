from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from datetime import date
from .models import Listing, User, Comment, Bid

from .models import User

categories = [
    ('SUV', "SUV"),
    ("Sedan", "Sedan"),
    ("Convertible", "Convertible"),
    ("Pickup Truck", "Pickup Truck"),
    ("Motorcycle", "Motorcycle"),
    ("Sports car", "Sports car"),
    ("Coupe", "Coupe")
]

listing_categories = ["SUV", "Sedan", "Convertible","Pickup Truck", "Motorcycle", "Sports car", "Coupe"]

class Add_Bid(forms.Form):
    title = forms.CharField(label='Listing title', widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'Title'}))
    description = forms.CharField(label='Listing description', widget=forms.Textarea(attrs={'name':'body', 'rows':5, 'cols':45, 'placeholder':'Description'}))
    year = forms.IntegerField(label='Production year',widget=forms.NumberInput(attrs={'autocomplete':'off', 'placeholder':'Year'}))
    bid = forms.IntegerField(label='Starting bid',widget=forms.NumberInput(attrs={'autocomplete':'off', 'placeholder':'Starting bid'}))
    link = forms.URLField(label="Photo link", widget=forms.URLInput(attrs={'autocomplete':'off', 'placeholder':'URL of photo'}), required=False)
    category = forms.CharField(label="Category", widget=forms.Select(choices=categories))

def index(request):
    listings = Listing.objects.filter(closed=False).order_by("-id")
    return render(request, "auctions/index.html", {
        "categories": listing_categories,
        "listings": listings
    })
    
@login_required
def my_listings(request):
    listings = request.user.listings.all().order_by("-id")
    print(listings)
    return render(request, "auctions/index.html", {
        "categories": listing_categories,
        "listings": listings
    })

def view_category(request, category):
    listings = Listing.objects.filter(closed=False, category=category).order_by("-id")
    return render(request, "auctions/index.html",{
        "categories": listing_categories,
        "listings": listings
    })

@login_required
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
            year = form.cleaned_data["year"]
            bid = form.cleaned_data["bid"]
            url = form.cleaned_data["link"]
            category = form.cleaned_data["category"]
            today = date.today()
            today_text = today.strftime("%d %B %Y")
            if url == "" or url == None:
                url = "https://media.istockphoto.com/id/1392182937/vector/no-image-available-photo-coming-soon.jpg?s=612x612&w=0&k=20&c=3vGh4yj0O2b4tPtjpK-q-Qg0wGHsjseL2HT-pIyJiuc="
            #create a preview of the description for the index
            preview_description = description[:100]
            if len(preview_description) == 100:
                 preview_description += "..."
            #create the new listing
            listing = Listing(title=title, description=description, preview_description=preview_description, year=year, bid=bid, photo_url=url, category=category, creation_date=today_text)
            listing.save()
            # Add the newly created listing to the listings field of the current user
            request.user.listings.add(listing)
            
            return HttpResponseRedirect(reverse("index"))
        new_form = Add_Bid()
        return render(request, "auctions/create.html", {"message": "The title, description, and bid sections are mandatory", "form": new_form})

@login_required       
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
        highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']
        comments = listing.comments.all().order_by("-id")
        user_listings = request.user.listings.all()
        if listing.closed:
            highest_bid_obj = Bid.objects.filter(listing=listing).order_by('-amount').first()
            if highest_bid_obj:
                highest_bidder = highest_bid_obj.user
                print(highest_bidder.username + "!!!!!")
            else:
                highest_bidder = None
            return render(request, "auctions/listing.html", {
        "winner" : highest_bidder,
        "listing": listing,
        "comments": comments,
        "highest_bid": highest_bid
        })
        else:
            highest_bidder = None
        if listing in user_listings:
            listing_admin = True
        else:
            listing_admin = False
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "creator": listing_admin,
            "comments": comments,
            "highest_bid": highest_bid
        })

@login_required    
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse(view_listing, args=(listing_id,)))

@login_required
def view_watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "watchlist" : watchlist
    })
    
@login_required
def add_bid(request, listing_id):
    #get the input from form
    bid = int(request.POST["bid"])
    listing = Listing.objects.get(pk=listing_id)
    if listing.closed:
        return HttpResponseRedirect(reverse(view_listing, args=(listing.id,)))
    user = request.user
    #check if the amount is bigger than the starting price, else return an error
    if listing.bid > bid:
        listing = Listing.objects.get(pk=listing_id)
        comments = listing.comments.all()
        user = request.user
        user_listings = request.user.listings.all()
        if listing in user_listings:
            listing_admin = True
        else:
            listing_admin = False
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "creator": listing_admin,
            "comments": comments,
            "msg": "Bid must be higher than starting bid"
        })
    #get other bids for the listing and see if this one is the highest, else return an error
    highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']
    try:
        if highest_bid > bid:
            listing = Listing.objects.get(pk=listing_id)
            comments = listing.comments.all()
            return render(request, "auctions/listing.html", {
            "listing": listing,
            "creator": listing_admin,
            "comments": comments,
            "msg": "Higher bid already exists"
            })
    except:
        pass
    #save the bid and redirect the user to the listing
    final_bid = Bid(user=user, listing=listing, amount=bid)
    final_bid.save()
    return HttpResponseRedirect(reverse(view_listing, args=(listing_id,)))

@login_required
def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.closed = True
    listing.save()
    return HttpResponseRedirect(reverse(index))

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

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import F

from .models import *


class Listing_form(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=10, min_value=0.01)
    image_url = forms.URLField(required=False)
    category = forms.ChoiceField(choices=[
        ('fashion', 'Fashion'),
        ('toys', 'Toys'),
        ('electronics', 'Electronics'),
        ('home', 'Home'),
        # Add more categories as needed
    ], required=False)



def index(request):
    active_listings = Auction.objects.filter(active_status = True).order_by('posted_at')
    if request.method == "POST":
        auction_id = request.POST.get('auction_id')
        auction = Auction.objects.get(pk = auction_id)
        auction.active_status = False
        auction.save()
        closed_listings =  Auction.objects.filter(active_status = False).order_by('posted_at')
        return render(request, "auctions/closed.html", {'active_listings': closed_listings})       
    else: 
        return render(request, "auctions/index.html", {'active_listings': active_listings})




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
def create_listing(request):
    if request.method == 'POST':
        form = Listing_form(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data['title']
            price = form.cleaned_data['starting_bid']
            picture = form.cleaned_data['image_url']
            category = form.cleaned_data['category']
            description = form.cleaned_data['description']

            new_item = Auction(
                user = user,
                item = title,
                price = price,
                description = description,
                picture = picture,
                category = category
            )
            new_item.save()
            # Process the form data here (e.g., save to the database)
            # Example: title = form.cleaned_data['title']
            #          description = form.cleaned_data['description']
            #          starting_bid = form.cleaned_data['starting_bid']
            #          image_url = form.cleaned_data['image_url']
            #          category = form.cleaned_data['category']
            #          ... (save data to the database)
            return HttpResponseRedirect(reverse("index"))

    else:
        form = Listing_form()
        return render(request, 'auctions/listing.html', {'form': form})
    
def item(request, auction_id):
    item = Auction.objects.get(pk = auction_id)
    watchlist_list = None
    bid_count = None
    highest_bid = Bid.objects.filter(auction=item).order_by('bid_price').first()
    winner = None
    if highest_bid is not None:
        winner = highest_bid.user
    if request.user.is_authenticated:
        watchlist_list = Watchlist.objects.filter(user = request.user, list = item).exists()
        bid_count = Bid.objects.filter(auction = item).count()
    if request.method == "POST":
        comment_text = request.POST.get('Comment')
        del_comm_id = request.POST.get('comment_id')
        if comment_text:
            user = request.user
            new_comment = Comment(
                user = user,
                auction = item,
                text = comment_text
            )
            new_comment.save()
        if del_comm_id:
            del_comm = Comment.objects.get(id = del_comm_id)
            del_comm.delete()
        comments = Comment.objects.filter(auction = item).order_by("created_at").all()
        return render (request, 'auctions/item.html',{'listing': item, "watchlist": watchlist_list, "bid_count": bid_count, "comments":comments, "winner":winner})
    else:
        comments = Comment.objects.filter(auction = item).order_by("created_at")
        return render (request, 'auctions/item.html',{'listing': item, "watchlist": watchlist_list, "bid_count": bid_count, "comments":comments,  "winner":winner})


def watchlist(request):
    if request.method == "POST":
        auction_id = request.POST.get('auction_id')
        auction = Auction.objects.get(pk=auction_id)
        #auction = get_object_or_404(Auction, pk=auction_id)
        #item = Watchlist.objects.order_by('watchlisted_at').filter(user = request.user).all()
        #item_list = Auction.Watchlist_items.all()
        watchlist_list = Watchlist.objects.filter(user = request.user, list = auction).exists()
        if not watchlist_list:
            Watchlist.objects.create(user=request.user, list=auction)
        else:
            watchlist_list = Watchlist.objects.filter(user = request.user, list = auction)
            watchlist_list.delete()
        return HttpResponseRedirect(reverse('watchlist'))

    item = Watchlist.objects.order_by('watchlisted_at').filter(user = request.user).all()
    return render(request, "auctions/watchlist.html", {'active_listings': item})

def bid(request):
    if request.method == "POST":
        bid_price = request.POST.get("Bid")
        auction_id = request.POST.get('auction_id')
        auction = Auction.objects.get(pk=auction_id)
        watchlist_list = Watchlist.objects.filter(user = request.user, list = auction).exists()
        bid_count = Bid.objects.count()
        try:
            if float(bid_price) <= float(auction.price):
                #return render(request, 'auctions/item.html', {'alert_message': "Your bid price is lower than the earlier bids or auction starting bid Price"})
                return render (request, 'auctions/item.html',{'listing': auction, "watchlist": watchlist_list,"bid_count": bid_count, 'alert_message': "Your bid price is lower than the earlier bids or auction starting bid Price"})
            else:
                new_bid = Bid(
                    user = request.user,
                    auction = auction,
                    bid_price = bid_price,
                )
                new_bid.save()
                auction.price = bid_price
                auction.save()
                return render (request, 'auctions/item.html',{'listing': auction, "watchlist": watchlist_list,"bid_count": bid_count, 'alert_message': "You have successfully placed the bid"})
        except ValueError:
            return render (request, 'auctions/item.html',{'listing': auction, "watchlist": watchlist_list,"bid_count": bid_count, 'alert_message': "You have submitted an empty form"})
        
def closed(request):
    closed_listings = Auction.objects.filter(active_status = False).order_by('posted_at')
    bid = Bid.objects.filter(auction__active_status = False).filter(auction__price = F("bid_price")).order_by('bidden_at')

    return render(request, "auctions/closed.html", {'active_listings': closed_listings, 'bid': bid})

def category(request, Category):
    active_listings = Auction.objects.filter(active_status = True).filter(category = Category).order_by('posted_at')
    return render(request, "auctions/index.html", {'active_listings': active_listings})

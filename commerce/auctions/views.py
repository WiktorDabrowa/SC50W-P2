
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import listingForm, bidForm, CommentForm
from .models import Listing, Bid, Comment
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import User



def index(request):
    listings = Listing.objects.filter(is_open = True)
    context = {'listings': listings, 'message':'All Active Listings'}
    return render(request, "auctions/index.html", context)


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

@login_required(login_url='/login')
def add_listing(request):
    
    if request.method == 'POST':
        form = listingForm(request.POST)
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            form.save()
            listing = Listing.objects.last()
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Please fill out all of the fields correctly!')
            return redirect("add")
    else:
        form = listingForm()
        context = {'form': form}
        return render(request, "auctions/add_listing.html", context)

def listing_page(request, pk):

    listing_item = Listing.objects.get(id=pk)
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing=listing_item)
    user = request.user
    watchable = False
    if user.is_authenticated:
        current_watchlist = user.watchlist.all()
        if listing_item in current_watchlist: 
            watchable = False
        else:
            watchable = True

    # Handling comments:
    if request.method == "POST":
        form = CommentForm(request.POST)
        comment = form.save(commit=False)
        comment.user = request.user
        comment.listing = listing_item
        if form.is_valid():
            comment.save()
            return HttpResponseRedirect(f'/item/{listing_item.id}')
    try:
        current_bid = Bid.objects.get(listing=listing_item)
        bid = True
    except ObjectDoesNotExist:
        bid = False
        current_bid = None
    if listing_item.seller == request.user:
        closable = True
    else:
        closable = False
    if listing_item.winner == request.user:
        message = "Congratulations, You have won this auction!"
    else:
        message=""
    context = {
        'item':listing_item,
        'close':closable,
        'current_bid':current_bid,
        'message':message,
        'comment_form':comment_form,
        'comments': comments,
        'watchable': watchable,
        'bid': bid}
    return render(request, 'auctions/listing.html', context)

@login_required(login_url='/login')
def bid(request, pk):
    form = bidForm()
    listing_item = Listing.objects.get(id=pk)
    try:
        current_bid = Bid.objects.get(listing=listing_item)
        bid = True
    except ObjectDoesNotExist:
        current_bid = None
        bid = False
    # Checking if user placing bid
    # is not the same as selling item
    if listing_item.seller == request.user:
        messages.error(request, 'You can not bid your own item!')
        return redirect(f"/item/{listing_item.id}")

    # Processing the form
    if request.method == "POST":
        form = bidForm(request.POST)
        bid = form.save(commit=False)
        bid.listing = listing_item
        bid.bidder = request.user

        if bid.price <= listing_item.starting_price:
            messages.error(request, 'Your bid must be higher than starting and current price!')
            return redirect(f'/item/{listing_item.id}/bid')

        if current_bid is not None:
            # Checking if bidder is not beating his own bid
            if current_bid.bidder == bid.bidder:
                messages.error(request, 'You tried to beat your own bid!')
                return redirect(f'/item/{listing_item.id}/bid')

            # Checking if placed bid is higher than previous
            if bid.price <= current_bid.price:
                messages.error(request, 'Your bid must be higher than the previous one!')
                return redirect(f'/item/{listing_item.id}/bid')

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/item/{listing_item.id}')

    context = {
        'item':listing_item,
        'form':form,
        'current_bid':current_bid,
        'bid':bid,
        
        }
    return render(request, "auctions/bid.html", context)

@login_required(login_url='/login')
def close(request, pk):
    listing_item = Listing.objects.get(id=pk)

    # Checking if user is the same as listing creator
    if listing_item.seller == request.user:
        listing_item.is_open = False
        # Setting the listing instance field 'winner' as 
        # current highest bidder
        listing_item.winner = listing_item.current_bid.bidder
        listing_item.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        messages.error(request, 'You are not the owner of the item, you cannot close this auction!')
        return redirect(f"/item/{listing_item.id}")
def category_list(request):
    category_list = Listing.objects.values_list('category', flat=True)
    category_list = list(set(category_list))
    return render(request, 'auctions/categories.html', {'categories': category_list})

def category_index(request, cat):
    listings = Listing.objects.filter(category=cat, is_open=True)
    context = {'listings': listings, 'message':f'Active Listings in Category: {cat}'}

    # Checking if queried category exist
    if cat not in Listing.objects.values_list('category', flat=True):
        raise Http404('Category does not exist!')
    
    # Checking if queried category has any active auctions
    if not listings:
        message = 'No active listings in this category'
        context = {'listings': listings,'message':message}
    return render(request, "auctions/index.html", context)

@login_required(login_url='/login')
def watchlist(request):
    user = request.user
    listings = user.watchlist.all()
    context = {'listings': listings, 'message':'Listings watched by You'}
    return render(request, 'auctions/watchlist.html', context)

@login_required(login_url='/login')
def watchlist_add(request, pk):
    user = request.user
    item = Listing.objects.get(id=pk)
    user.watchlist.add(item)
    return HttpResponseRedirect(f'/item/{pk}')

@login_required(login_url='/login')
def watchlist_remove(request, pk):
    user = request.user
    item = Listing.objects.get(id=pk)
    user.watchlist.remove(item)
    return redirect(request.META.get('HTTP_REFERER', '/'))
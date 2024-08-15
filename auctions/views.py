from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import User, Category, Listing, Bid, Comment, BidHistory
from .forms import ListingForm, BidForm, CommentForm
    
def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    watchlist = request.user.followed_listings.all() if request.user.is_authenticated else []

    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "watchlist": watchlist,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
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
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
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
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.current_price = listing.starting_bid
            listing.starting_price = listing.starting_bid
            listing.save()
            return redirect('listing', listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})

# def listing(request, listing_id):
#     listing = get_object_or_404(Listing, pk=listing_id)
#     in_watchlist = request.user.is_authenticated and request.user.followed_listings.filter(pk=listing_id).exists()
#     comments = Comment.objects.filter(listing=listing).order_by('-created_at')
#     bid_form = BidForm()
#     comment_form = CommentForm()

#     if request.method == "POST":
#         if "bid" in request.POST and request.user.is_authenticated:
#             if "bid" in request.POST and request.user.is_authenticated:
#                 bid_form = BidForm(request.POST)
#                 if bid_form.is_valid():
#                     bid = bid_form.save(commit=False)
#                     bid.user = request.user
#                     bid.listing = listing
                    
#                     if request.user == listing.creator:
#                         listing.current_price = bid.amount
#                         listing.save()
#                         messages.success(request, "Precio actualizado correctamente.")
#                     elif bid.amount >= listing.current_price:
#                         bid.save()
#                         listing.current_price = bid.amount
#                         listing.save()
#                         messages.success(request, "Oferta realizada correctamente.")
#                     else:
#                         messages.error(request, "La oferta debe ser al menos igual al precio actual.")

#                     return redirect('listing', listing_id=listing_id)
#                 else:
#                     messages.error(request, "Formulario de oferta inválido. Por favor, inténtalo de nuevo.")

        
#         elif "comment" in request.POST and request.user.is_authenticated:
#             comment_form = CommentForm(request.POST)
#             if comment_form.is_valid():
#                 comment = comment_form.save(commit=False)
#                 comment.user = request.user
#                 comment.listing = listing
#                 comment.save()
#                 messages.success(request, "Comentario añadido correctamente.")
#                 return redirect('listing', listing_id=listing_id)
#             else:
#                 messages.error(request, "Formulario de comentario inválido. Por favor, inténtalo de nuevo.")
        
#         elif "close" in request.POST and request.user == listing.creator:
#             if Bid.objects.filter(listing=listing).exists():
#                 listing.is_active = False
#                 listing.winner = Bid.objects.filter(listing=listing).order_by('-amount').first().user
#                 listing.save()
#                 messages.success(request, "Subasta cerrada correctamente.")
#             else:
#                 listing.is_active = False
#                 listing.save()
#                 messages.info(request, "La subasta ha sido suspendida temporalmente, ya que no se recibieron ofertas.")
#             return redirect('listing', listing_id=listing_id)


#     context = {
#         "listing": listing,
#         "in_watchlist": in_watchlist,
#         "comments": comments,
#         "bid_form": bid_form,
#         "comment_form": comment_form
#     }
#     return render(request, "auctions/listing.html", context)

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    in_watchlist = request.user.is_authenticated and request.user.followed_listings.filter(pk=listing_id).exists()
    comments = Comment.objects.filter(listing=listing).order_by('-created_at')
    bid_form = BidForm()
    comment_form = CommentForm()

    if request.method == "POST":
        if "bid" in request.POST and request.user.is_authenticated:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.user = request.user
                bid.listing = listing
                
                if request.user == listing.creator:
                    listing.current_price = bid.amount
                    listing.save()
                    messages.success(request, "Precio actualizado correctamente.")
                elif bid.amount >= listing.current_price:
                    bid.save()
                    # Guardar en el historial de ofertas
                    BidHistory.objects.create(
                        listing=listing,
                        bidder=request.user,
                        bid_amount=bid.amount
                    )
                    listing.current_price = bid.amount
                    listing.save()
                    messages.success(request, "Oferta realizada correctamente.")
                else:
                    messages.error(request, "La oferta debe ser al menos igual al precio actual.")

                return redirect('listing', listing_id=listing_id)
            else:
                messages.error(request, "Formulario de oferta inválido. Por favor, inténtalo de nuevo.")

        elif "comment" in request.POST and request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.listing = listing
                comment.save()
                messages.success(request, "Comentario añadido correctamente.")
                return redirect('listing', listing_id=listing_id)
            else:
                messages.error(request, "Formulario de comentario inválido. Por favor, inténtalo de nuevo.")
        
        elif "close" in request.POST and request.user == listing.creator:
            if Bid.objects.filter(listing=listing).exists():
                listing.is_active = False
                listing.winner = Bid.objects.filter(listing=listing).order_by('-amount').first().user
                listing.save()
                messages.success(request, "Subasta cerrada correctamente.")
            else:
                listing.is_active = False
                listing.save()
                messages.info(request, "La subasta ha sido suspendida temporalmente, ya que no se recibieron ofertas.")
            return redirect('listing', listing_id=listing_id)
        
    bid_history = BidHistory.objects.filter(listing=listing).order_by('-timestamp')
    bids = listing.bids.order_by('-amount')
    initial_price = listing.starting_price
    highest_bid = bids.first() if bids else None
    other_bids = bids[1:] if bids.count() > 1 else []
    
    context = {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "comments": comments,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "bid_history": bid_history,
        'initial_price': initial_price,
        'highest_bid': highest_bid,
        'other_bids': other_bids,
    }
    return render(request, "auctions/listing.html", context)


@login_required
def watchlist(request):
    followed_listings = request.user.followed_listings.all()
    return render(request, 'auctions/watchlist.html', {
        'followed_listings': followed_listings
    })

@login_required(login_url='/login/')
def toggle_watchlist(request, listing_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to add items to your watchlist.")
        print("Mensaje enviado")
        return redirect('login') 
    # if not request.user.is_authenticated:
    #     messages.error(request, 'Debes iniciar sesión para añadir ítems a tu lista de seguimiento.')
    #     return redirect('login')
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.user.followed_listings.filter(pk=listing_id).exists():
        request.user.followed_listings.remove(listing)
    else:
        request.user.followed_listings.add(listing)
    return redirect('listing', listing_id=listing_id)

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })
    
def example_view(request):
    messages.error(request, 'Este es un mensaje de prueba.')
    return redirect('index')

def some_view(request):
    messages.success(request, "Este es un mensaje de prueba.")
    return render(request, 'index.html')

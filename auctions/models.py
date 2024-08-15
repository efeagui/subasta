from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    followed_listings = models.ManyToManyField('Listing', related_name='followers', blank=True)

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image_url = models.URLField(blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_listings')
    
    def save(self, *args, **kwargs):
        if self.starting_price is None:
            self.starting_price = self.starting_bid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BidHistory(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_history")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} offered ${self.bid_amount} on {self.timestamp}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, related_name='bids', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} - ${self.amount}"
    
class Comment(models.Model):
    listing = models.ForeignKey(Listing, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.content[:20]}"
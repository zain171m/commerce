from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Seller")
    item = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10 , decimal_places=2)
    description = models.CharField(max_length=200)
    #picture = models.ImageField(upload_to='auctions/auction_pictures/', blank=True, null=True)
    picture = models.URLField(blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=64, blank = True)
    active_status = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.user} is selling {self.item} for {self.price}"
    

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Buyer")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="sale_item")
    bid_price = models.DecimalField(max_digits=10 , decimal_places=2)
    bidden_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bidden {self.bid_price} for {self.auction.item}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Commentator")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commented_item")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented {self.text} on {self.auction.item}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Watchlister")
    list = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="Watchlist_items")
    watchlisted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} watchlisted {self.list.item} on {self.watchlisted_at}"   
    
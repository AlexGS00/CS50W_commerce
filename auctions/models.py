from django.contrib.auth.models import AbstractUser
from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=5000)
    preview_description = models.CharField(max_length=110, default="Coming soon")
    photo_url = models.CharField(max_length=500, blank=True)
    year = models.IntegerField()
    bid = models.IntegerField()
    category = models.CharField(max_length=30)
    creation_date = models.CharField(max_length=64)
    closed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} : {self.title}"

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, blank=True, related_name="watchlist")
    listings = models.ManyToManyField(Listing, blank=True, related_name="listings")
    pass

class Comment(models.Model):
    text = models.CharField(max_length=500)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.CharField(max_length=64)
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()
    
    def __str__(self):
        return f"{self.listing}: ${self.amount} by {self.user}"

from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing')
    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(default = 'Description',max_length=500,)
    category = models.CharField(max_length = 64, default = 'Category', blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    added = models.DateTimeField(auto_now_add=True)
    photo = models.CharField(max_length=2000, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="is_selling")
    is_open = models.BooleanField(default=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="winner")
    
    def describe(self):
        return self.description[0:40]

    def __str__(self):
        if self.is_open == True:
            return f"{self.title} | OPEN"
        else:
            return f"{self.title} | CLOSED"

        
class Bid(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, primary_key=True, related_name = "current_bid")
    price = models.DecimalField(max_digits=10, decimal_places=2,)
    last_modified = models.DateField(auto_now=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="is_bidding")


    def __str__(self):
        return f"{self.listing} | {self.bidder} | {self.price}$"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.CharField(max_length=200)
    added = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.listing} | {self.user} |{self.body[0:50]}"
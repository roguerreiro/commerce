from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    image = models.URLField(max_length=300, blank=True)
    category = models.CharField(max_length=25)
    date = models.DateField()
    time = models.TimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.item


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    starterbid = models.DecimalField(decimal_places=2, max_digits=8)
    bid = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return self.auction.item


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return self.auction.item + '(' + self.commenter.username + ')'

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.auction.item

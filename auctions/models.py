from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}: {self.username}"


class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellers")
    title = models.CharField(max_length=200)
    description = models.TextField()
    startBid = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    belonging = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    curBid = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"{self.bidder.username} rasing a paddle for {self.belonging.title}: {self.curBid}"


class Watchlist(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owners")
    belonging = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="belongings")
    
    class Meta:
        unique_together = ('creator', 'belonging')

    def __str__(self):
        return f"{self.creator.username}'s Watchlist"
        

class Comment(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writers")
    target = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="targets")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.writer.username} wrote for {self.target.title}"

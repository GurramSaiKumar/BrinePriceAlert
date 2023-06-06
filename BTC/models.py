from django.db import models
from django.contrib.auth.models import User


class PriceAlert(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cryptocurrency = models.CharField(max_length=100)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='created')

    def __str__(self):
        return f"{self.user} - {self.cryptocurrency} - {self.target_price}"

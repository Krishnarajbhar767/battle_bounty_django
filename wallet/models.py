from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    deposit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    winning_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_frozen = models.BooleanField(default=False)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email}'s wallet"


class Transaction(models.Model):
    TYPE_CHOICES = [('credit', 'Credit'), ('debit', 'Debit')]
    STATUS_CHOICES = [('pending', 'Pending'), ('failed', 'Failed'), ('success', 'Success')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    tournament = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=50, blank=True,null=True)
    screenshot = models.URLField(blank=True)
    utr_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} | {self.type} | {self.amount}"

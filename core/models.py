from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class LoanRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.status}"

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        MANAGER = 'MANAGER', 'Bank Manager'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_manager(self):
        return self.role == self.Role.MANAGER

class BankAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_frozen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

class Transaction(models.Model):
    from_account = models.ForeignKey(BankAccount, related_name='sent_transactions', on_delete=models.CASCADE)
    to_account = models.ForeignKey(BankAccount, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_account.user.username} -> {self.to_account.user.username}: {self.amount} on {self.timestamp}"

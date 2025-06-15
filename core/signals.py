from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, BankAccount

@receiver(post_save, sender=CustomUser)
def create_bank_account(sender, instance, created, **kwargs):
    if created and instance.role == CustomUser.Role.CUSTOMER:
        account, created_account = BankAccount.objects.get_or_create(user=instance)
        print(f"DEBUG Signal: BankAccount created? {created_account} for user {instance.username}")

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import LoanRequest
from decimal import Decimal
from .models import BankAccount  # ✅ import BankAccount

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['amount', 'reason']
        
class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label="Deposit Amount"
    )
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Deposit amount must be positive.")
        return amount


class CustomerSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.CUSTOMER
        if commit:
            user.save()
            # Only create BankAccount if it doesn't exist
            if not BankAccount.objects.filter(user=user).exists():
                BankAccount.objects.create(user=user)
        return user

class FundTransferForm(forms.Form):
    to_username = forms.CharField(label="Recipient Username")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount

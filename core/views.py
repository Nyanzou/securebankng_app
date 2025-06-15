# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import FundTransferForm, DepositForm, CustomerSignUpForm
from .models import BankAccount, Transaction, CustomUser
from .forms import LoanRequestForm
from .models import LoanRequest


# ✅ Home Page
def home(request):
    return render(request, 'core/home.html')


# ✅ Customer Registration View
def customer_register(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomerSignUpForm()
    return render(request, 'core/customer_register.html', {'form': form})


# ✅ Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == CustomUser.Role.CUSTOMER:
                return redirect('customer_dashboard')
            elif user.role == CustomUser.Role.MANAGER:
                return redirect('manager_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


# ✅ Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# ✅ Customer Dashboard View (Deposit + Transfer)
@login_required
def loan_request_view(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.save()
            messages.success(request, "Loan request submitted successfully.")
            return redirect('customer_dashboard')
    else:
        form = LoanRequestForm()

    user_loans = LoanRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'core/loan_request.html', {
        'form': form,
        'user_loans': user_loans
    })
def customer_dashboard(request):
    user = request.user
    try:
        account = BankAccount.objects.get(user=user)
    except BankAccount.DoesNotExist:
        messages.error(request, "Bank account not found.")
        return redirect('home')

    transfer_form = FundTransferForm()
    deposit_form = DepositForm()

    if request.method == 'POST':
        if 'transfer_submit' in request.POST:
            transfer_form = FundTransferForm(request.POST)
            if transfer_form.is_valid():
                to_username = transfer_form.cleaned_data['to_username']
                amount = transfer_form.cleaned_data['amount']

                try:
                    recipient_user = CustomUser.objects.get(username=to_username)
                    if recipient_user.role != CustomUser.Role.CUSTOMER:
                        raise CustomUser.DoesNotExist
                    recipient_account = BankAccount.objects.get(user=recipient_user)

                    if recipient_user == user:
                        messages.error(request, "You can't send money to yourself.")
                    elif account.balance < amount:
                        messages.error(request, "Insufficient funds.")
                    else:
                        account.balance -= amount
                        recipient_account.balance += amount
                        account.save()
                        recipient_account.save()

                        Transaction.objects.create(
                            from_account=account,
                            to_account=recipient_account,
                            amount=amount
                        )
                        messages.success(request, f"${amount} sent to {to_username}.")
                        return redirect('customer_dashboard')

                except CustomUser.DoesNotExist:
                    messages.error(request, "Recipient not found or not a customer.")
                except BankAccount.DoesNotExist:
                    messages.error(request, "Recipient's bank account not found.")

        elif 'deposit_submit' in request.POST:
            deposit_form = DepositForm(request.POST)
            if deposit_form.is_valid():
                amount = deposit_form.cleaned_data['amount']
                account.balance += amount
                account.save()
                messages.success(request, f"${amount} deposited successfully!")
                return redirect('customer_dashboard')

    transactions_sent = Transaction.objects.filter(from_account=account).order_by('-timestamp')[:5]
    transactions_received = Transaction.objects.filter(to_account=account).order_by('-timestamp')[:5]

    return render(request, 'core/customer_dashboard.html', {
        'account': account,
        'form': transfer_form,
        'deposit_form': deposit_form,
        'transactions_sent': transactions_sent,
        'transactions_received': transactions_received,
    })


# ✅ Manager Dashboard View
@login_required
def manager_dashboard(request):
    if not request.user.is_authenticated or request.user.role != CustomUser.Role.MANAGER:
        messages.error(request, "Access denied.")
        return redirect('home')

    accounts = BankAccount.objects.all().select_related('user')
    loans = LoanRequest.objects.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        # ✅ Handle Account actions
        account_id = request.POST.get('account_id')
        if account_id:
            try:
                account = BankAccount.objects.get(id=account_id)

                if action == 'approve':
                    account.is_approved = True
                    messages.success(request, f"{account.user.username}'s account approved.")
                elif action == 'deny':
                    account.user.delete()
                    messages.success(request, f"Account deleted.")
                elif action == 'freeze':
                    account.is_frozen = True
                    messages.success(request, f"{account.user.username}'s account frozen.")
                elif action == 'unfreeze':
                    account.is_frozen = False
                    messages.success(request, f"{account.user.username}'s account unfrozen.")

                account.save()

            except BankAccount.DoesNotExist:
                messages.error(request, "Account not found.")

        # ✅ Handle Loan actions
        loan_id = request.POST.get('loan_id')
        if loan_id:
            try:
                loan = LoanRequest.objects.get(id=loan_id)

                if action == 'approve':
                    loan.status = 'APPROVED'
                    messages.success(request, f"Loan approved for {loan.user.username}")
                elif action == 'deny':
                    loan.status = 'DENIED'
                    messages.success(request, f"Loan denied for {loan.user.username}")

                loan.save()

            except LoanRequest.DoesNotExist:
                messages.error(request, "Loan request not found.")

        return redirect('manager_dashboard')

    return render(request, 'core/manager_dashboard.html', {
        'accounts': accounts,
        'loans': loans,  # ✅ Now loans are available in the template
    })
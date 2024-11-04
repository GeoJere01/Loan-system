from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator as token_generator
from core.forms import LoanApplicationForm, PersonalBankDetailForm, UserForm, UserRegistrationForm
from core.models import Loan, Member, PersonalBankDetail

# Create your views here.

#------View for Full loan history-----
def home(request):
    return render(request, "index.html")
#------End of view for full loan history-----


def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back.')
                return redirect('home')  # Redirect to a success page
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password'})
        else:
            return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(Member, pk=uid)
    except (TypeError, ValueError, OverflowError, Member.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. You can now login to your account.')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def logout_view(request):
    logout(request)  # This logs out the user
    request.session.flush()
    messages.success(request, 'You logout successfully.')
    return redirect('login')  # Redirect to login page after logout


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is not active until they confirm their email
            user.save()
             # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = f"http://{current_site.domain}{activation_link}"

            message = render_to_string('email.txt', {
                'user': user,
                'activation_url': activation_url,
            })
            send_mail(mail_subject, message, 'stanislasnaxy@gmail.com',  [user.email])
            return render(request, 'login.html', {'message': 'Please confirm your email address to complete the registration.'}) # Redirect to login after successful registration
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def user_details(request, id):
    user = request.user

    try:
        # Get existing details if available
        personal_details = PersonalBankDetail.objects.get(member=request.user)
    except PersonalBankDetail.DoesNotExist:
        personal_details = None

    if request.method == 'POST':
        form = PersonalBankDetailForm(request.POST, instance=personal_details)
        nameform = UserForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            detail = form.save(commit=False)
            detail.member = request.user  # Corrected from detail.user to detail.member
            detail.save()

        if nameform.is_valid():
            nameform.save()
            messages.success(request, 'Your account has been successfully updated.')
            return redirect('home')   
    else:
        form = PersonalBankDetailForm(instance=personal_details)
        nameform = UserForm(instance=user)

    return render(request, "user.html", {'form': form, 'nameform': nameform, 'user': user,})



@login_required
def loans(request):
    user = request.user
    
    # Count the number of pending loan applications
    total_pending_loans = Loan.objects.filter(status='Pending').count()
    
    # Check if the user has any outstanding loans (excluding 'Rejected' and 'Paid')
    outstanding_loans = Loan.objects.filter(
        member=user, repaid=False
    ).exclude(status__in=['Rejected', 'Paid']).first()
    
    # Check if there are any rejected or pending loans
    rejected_loan = Loan.objects.filter(member=user, status='Rejected').first()
    pending_loan = Loan.objects.filter(member=user, status='Pending').first()

    # Calculate the outstanding amount and interest amount if there is an outstanding loan
    outstanding_amount = Decimal('0.00')
    interest_amount = Decimal('0.00')
    due_date = None
    status = None
    approved_amount = Decimal('0.00')

    if outstanding_loans:
        outstanding_amount = outstanding_loans.total_repayable - outstanding_loans.amount_paid
        interest_amount = outstanding_loans.total_repayable - outstanding_loans.amount  # Interest part
        due_date = outstanding_loans.date_due
        status = outstanding_loans.status
        approved_amount = outstanding_loans.amount

    user_loans = Loan.objects.filter(member=user).order_by('-date_issued')

    # Check if personal bank details exist
    try:
        personal_details = PersonalBankDetail.objects.get(member=user)
    except PersonalBankDetail.DoesNotExist:
        personal_details = None

    # Display the loan form only if there are no outstanding or pending loans
    show_loan_form = not outstanding_loans and not pending_loan

    if request.method == 'POST' and show_loan_form:
        loan_form = LoanApplicationForm(request.POST, request.FILES)
        bank_details_form = PersonalBankDetailForm(request.POST, instance=personal_details)
        
        if loan_form.is_valid() and bank_details_form.is_valid():
            # Save or update bank details
            bank_details = bank_details_form.save(commit=False)
            bank_details.member = user
            bank_details.save()

            # Save loan application with collateral information
            loan_application = loan_form.save(commit=False)
            loan_application.member = user
            loan_application.bank_details = bank_details

            # Convert amount and interest rate to Decimal
            loan_amount = Decimal(str(loan_application.amount))
            interest_rate = Decimal(loan_application.interest_rate) / 100

            # Calculate total repayment
            loan_application.total_repayment = loan_amount + (loan_amount * interest_rate)
            loan_application.save()

            messages.success(request, 'Loan application submitted successfully.')
            return redirect('home')  # Redirect to a suitable page after submission
    else:
        loan_form = LoanApplicationForm()
        bank_details_form = PersonalBankDetailForm(instance=personal_details)

    context = {
        'loan_form': loan_form,
        'bank_details_form': bank_details_form,
        'personal_details': personal_details,
        'user_loans': user_loans,
        'outstanding_loans': outstanding_loans is not None,
        'outstanding_amount': outstanding_amount,
        'interest_amount': interest_amount,
        'due_date': due_date,
        'status': status,
        'approved_amount': approved_amount,
        'rejected_loan': rejected_loan is not None,
        'pending_loan': pending_loan is not None,
        'total_pending_loans': total_pending_loans,
        'show_loan_form': show_loan_form,
    }
    return render(request, 'loan.html', context)
#-------End of view for loan------

from django import forms
from .models import  Loan, Member, PersonalBankDetail
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ['username','full_name','email','phone_number','gender','occupation','id_type', 'id_number', 'address','city','state', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter user email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'occupation': forms.TextInput(attrs={'placeholder': 'Enter your occupation'}),
            'id_number': forms.TextInput(attrs={'placeholder': 'Enter your id number'}),
            'address': forms.TextInput(attrs={'placeholder': '1234 Main St'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter your state'}),
            'password1': forms.TextInput(attrs={'placeholder': 'Enter user password'}),
            'password2': forms.TextInput(attrs={'placeholder': 'Confirm user password'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['username', 'full_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter user email'}),
        }

class PersonalBankDetailForm(forms.ModelForm):
    class Meta:
        model = PersonalBankDetail
        fields = ['bank_name', 'account_number', 'account_name', 'branch']
        widgets = {
            'account_number': forms.NumberInput(attrs={'placeholder': 'Account Number'}),
            'account_name': forms.TextInput(attrs={'placeholder': 'Enter account name'}),
            'branch': forms.TextInput(attrs={'placeholder': 'Enter bank branch'}),
            'bank_name': forms.TextInput(attrs={'placeholder': 'Enter bank name'}),
            
        }

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'collateral_name', 'collateral_description', 'collateral_image']  # Include the new fields

        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter loan amount'}),
            'collateral_name': forms.TextInput(attrs={'placeholder': 'Enter collateral name'}),
            'collateral_description': forms.Textarea(attrs={'placeholder': 'Enter collateral description', 'rows': 4}),
        }

class LoanManagementForm(forms.ModelForm):
    """Form for executive members to manage loan details, including setting the loan date."""
    class Meta:
        model = Loan
        fields = ['member','collateral_name', 'collateral_description' , 'collateral_image', 'amount', 'date_issued']  # Include date_issued for executives


class LoanRepaymentForm(forms.ModelForm):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Repayment Amount")

    class Meta:
        model = Loan
        fields = ['member','amount']
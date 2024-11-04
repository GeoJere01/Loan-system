from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

from loan_system import settings

class Member(AbstractUser):
    STATUS_CHOICES = (
        ('---Select---', '---Select---'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    ID_CHOICES = (
        ('---Select---', '---Select---'),
        ('National ID', 'National ID'),
        ('Passport', 'Passport'),
        ('License', 'License'),
    )
    full_name = models.CharField(max_length=100, default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=50, choices=STATUS_CHOICES, default='---Select---', null=True)
    occupation = models.CharField(max_length=255, default=None,null=True)
    id_type = models.CharField(max_length=50, choices=ID_CHOICES, default='---Select---',null=True)
    id_number = models.CharField(max_length=255, default=None,null=True)
    address = models.CharField(max_length=255, default=None,null=True)
    city = models.CharField(max_length=255, default=None,null=True)
    state = models.CharField(max_length=255, default=None,null=True)


    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='user',
    )

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        managed = True
        ordering = ['id']



class Loan(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    collateral_description = models.CharField(max_length=255, blank=True, null=True)
    collateral_name = models.CharField(max_length=255, blank=True, null=True)
    collateral_image = models.ImageField(upload_to='collateral_images/', default=None)
    date_issued = models.DateField(null=True, blank=True, help_text="Date the loan was issued")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    date_due = models.DateField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    total_repayable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
    repaid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Track repayments
    rejection_reason = models.CharField(max_length=255,null=True, blank=True)  # Add field for rejection reason

    REQUIRED_APPROVALS = 2  # Define the number of required approvals

    def record_repayment(self, amount):
        """Record a repayment and update the loan status only if fully paid."""
        if amount > 0:
            self.amount_paid += Decimal(amount)  # Add repayment to the amount paid
            self.total_repayable -= Decimal(amount)  # Subtract repayment from the total repayable
            
            # If the loan is fully paid, update the status to 'Paid'
            if self.amount_paid >= self.total_repayable:
                self.amount_paid = self.total_repayable  # Ensure the paid amount does not exceed total repayable
                self.status = 'Paid'  # Set status to Paid
                self.repaid = True  # Mark the loan as repaid
            
            self.save()  # Save the updated loan details
        else:
            raise ValueError("Repayment amount must be positive.")
    
    @property
    def remaining_amount(self):
        """Calculate the remaining loan amount to be paid."""
        return max(self.total_repayable - self.amount_paid, Decimal('0.00'))

    def calculate_total_repayable(self):
        """Calculate the total amount repayable including interest."""
        interest_amount = self.amount * (self.interest_rate / Decimal('100'))
        self.total_repayable = self.amount + interest_amount

    def apply_penalty(self):
        """Apply a penalty if the repayment is late by more than one month."""
        penalty_amount = self.total_repayable * (self.penalty_rate / Decimal('100'))
        self.total_repayable += penalty_amount
        self.save()


    def check_approval_status(self):
        """Check if the loan has enough approvals to be considered 'Approved'."""
        if self.approvals.count() >= self.REQUIRED_APPROVALS:
            self.status = 'Approved'
        else:
            self.status = 'Pending'
        self.save()

    def save(self, *args, **kwargs):
        # If the status is approved and date_issued is not set, set it to today's date
        if self.status == 'Approved' and not self.date_issued:
            self.date_issued = date.today()  # Set date_issued to the current date

        # Calculate the total repayable amount including interest
        self.calculate_total_repayable()

        # Ensure the loan must be repaid within 4 months of date_issued
        if self.status == 'Approved' and not self.date_due:
            self.date_due = self.date_issued + timedelta(days=90)  # 3 months

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan of {self.amount} for {self.member.full_name} due by {self.date_due}"

class PersonalBankDetail(models.Model):
    member = models.OneToOneField(Member, on_delete=models.SET_NULL, null=True, related_name='bank_details')
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.member.full_name}'s Bank Details"



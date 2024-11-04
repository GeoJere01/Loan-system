from django.contrib import admin

from core.models import Loan, Member, PersonalBankDetail

# Register your models here.

# Customize the admin panel
admin.site.site_header = "EasyPackBack Management Admin"
admin.site.site_title = "EasyPackBack Admin Portal"
admin.site.index_title = "Welcome to the EasyPackBackManagement Admin"



@admin.register(Member)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'username', 'email')
    # list_editable = ('is_executive',)  # Make penalty_amount editable


@admin.register(Loan)
class UserAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount','collateral_name','collateral_image', 'date_issued', 'date_due', 'total_repayable', 'amount_paid', 'status', 'rejection_reason' ,'repaid')
    list_editable = ('repaid','status','rejection_reason')  # Make penalty_amount editab


@admin.register(PersonalBankDetail)
class UserAdmin(admin.ModelAdmin):
    list_display = ('member','bank_name', 'account_number', 'account_name' ,'branch')

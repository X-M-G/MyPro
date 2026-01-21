from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from .models import CreditTransaction
from .forms import AddCreditsForm

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    class CreditTransactionInline(admin.TabularInline):
        model = CreditTransaction
        extra = 0
        readonly_fields = ('timestamp', 'description', 'balance_after')
        can_delete = False
        ordering = ('-timestamp',)

    inlines = [CreditTransactionInline]

    list_display = ('id', 'username', 'email', 'credits', 'invited_by', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'phone_number', 'invitation_code')
    ordering = ('id',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Extra Info'), {'fields': ('phone_number', 'invitation_code', 'invited_by', 'credits', 'password_verified_at')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'credits'),
        }),
    )
    
    actions = ['modify_credits_action']

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new and obj.credits > 0:
            CreditTransaction.objects.create(
                user=obj,
                amount=obj.credits,
                balance_after=obj.credits,
                description=_("Initial Credits (Admin Creation)")
            )

    @admin.action(description=_("Add/Deduct Credits"))
    def modify_credits_action(self, request, queryset):
        if 'apply' in request.POST:
            form = AddCreditsForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                description = form.cleaned_data['description']
                
                count = 0
                try:
                    with transaction.atomic():
                        for user in queryset:
                            user.credits += amount
                            user.save()
                            
                            CreditTransaction.objects.create(
                                user=user,
                                amount=amount,
                                balance_after=user.credits,
                                description=description
                            )
                            count += 1
                    
                    self.message_user(request, _("Successfully updated credits for %(count)d users.") % {'count': count}, messages.SUCCESS)
                    return HttpResponseRedirect(request.get_full_path())
                except Exception as e:
                    self.message_user(request, _("Error updating credits: %(error)s") % {'error': str(e)}, messages.ERROR)
                    return HttpResponseRedirect(request.get_full_path())
        else:
            form = AddCreditsForm()

        return render(request, 'admin/users/add_credits_form.html', {
            'users': queryset,
            'form': form,
            'title': _('Add/Deduct Credits'),
            'opts': self.model._meta,
        })

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'balance_after', 'description', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)

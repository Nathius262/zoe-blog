from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from profileAccount.models import Account, Follower


# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'name', 'date_joined', 'last_login', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


@admin.register(models.Follower)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'user')
    search_fields = ('follower', 'user')


admin.site.register(Account, AccountAdmin)

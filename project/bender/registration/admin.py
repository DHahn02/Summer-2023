from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class AccountsUserAdmin(AuthUserAdmin):
    def add_view(self, *arg, **kwargs):
        self.inlines = []
        return super(AccountsUserAdmin, self).add_view(*arg, **kwargs)

    def change_view(self, *arg, **kwargs):
        self.inlines = [UserProfileInline]
        return super(AccountsUserAdmin, self).change_view(*arg, **kwargs)


admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
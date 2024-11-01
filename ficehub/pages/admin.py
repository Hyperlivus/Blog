from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # Optionally customize the display of fields in the admin
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'birthdate')}),
    )

admin.site.register(User, CustomUserAdmin)
# Register your models here.

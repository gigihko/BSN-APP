from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Warga, Iuran, Pembayaran

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informasi Pribadi', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(Warga)
admin.site.register(Iuran)
admin.site.register(Pembayaran)

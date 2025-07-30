from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Warga, Iuran, Pembayaran

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Info Tambahan', {'fields': ('role', 'alamat')}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role',)

admin.site.register(User, UserAdmin)
admin.site.register(Warga)
admin.site.register(Iuran)
admin.site.register(Pembayaran)

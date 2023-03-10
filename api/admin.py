from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'username','pk', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Concert)
admin.site.register(models.Request)
admin.site.register(models.Service)
admin.site.register(models.Ticket)
admin.site.register(models.FavoriteConcert)
admin.site.register(models.FavoriteService)

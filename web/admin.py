from django.contrib import admin
from web.models import Client, UserBD


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Client, AuthorAdmin)
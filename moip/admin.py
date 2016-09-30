from django.contrib import admin

from moip.models import Moip

# Register your models here.
class AdminMoip(admin.ModelAdmin):
    list_display = ('titulo',
                    'razao',
                    'login_moip')
    list_filter = ('titulo',)

    filter_horizontal = ('formas_pagamento',) 

admin.site.register(Moip, AdminMoip)
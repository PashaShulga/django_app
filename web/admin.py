from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from web.models import Client, update_settings, Product
from django.db import connections
from django.conf import settings
from loginsys.form import UploadFileForm


class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'userdb'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    # def get_fields(self, request, obj=None):
    #     cursor = connections[self.using].cursor()
    #     query = super(MultiDBModelAdmin, self).get_queryset(request).using(self.using)
    #     id = []
    #     for q in query:
    #         cursor.execute("select * FROM product WHERE id=%s" % (q.id,))
    #         res = cursor.fetchall()
    #         id.append(str(res[0][0]))
    #     return UploadFileForm()

    def get_queryset(self, request):
        # cursor = connections[self.using].cursor()
        query = super(MultiDBModelAdmin, self).get_queryset(request).using(self.using)
        # for q in query:
            # cursor.execute("select * FROM product WHERE id=%s" % (q.id,))
            # q.__dict__['data'] = cursor.fetchall()
        return query

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)


# class ProductInlines(MultiDBTabularInline):
#     model = Product

from django.utils.html import format_html_join
from django.utils.safestring import mark_safe


class ProductAdmin(MultiDBModelAdmin):
    # fields = ('address_report',)

    def get_fields(self, request, obj=None):
        cursor = connections[self.using].cursor()
        cursor.execute("select * FROM product WHERE id=%s" % (obj.id,))
        # print(cursor.fetchall()[0])
        # d = format_html_join(mark_safe('<br/>'), '{}', ((line,) for line in cursor.fetchall()[0]),) or mark_safe("<span class='errors'>I can't determine this address.</span>")
        # print(d)
        print(cursor.fetchall()[0])
        return cursor.fetchall()[0]
    # address_report.short_description = "Address"


class ClientAdmin(admin.ModelAdmin):
    fields = ('address',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
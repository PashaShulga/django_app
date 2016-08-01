# from django.contrib import admin
# from web.models import Client
#
# #
# # class MultiDBModelAdmin(admin.ModelAdmin):
# #     # A handy constant for the name of the alternate database.
# #     # using = [un.username for un in UserBD.objects.all()]
# #     # for un in UserBD.objects.all():
# #     #         using = un.username
# #
# #     def delete_model(self, request, obj):
# #         # Tell Django to delete objects from the 'other' database
# #         obj.delete(using=self.using)
# #
# #     def get_queryset(self, request):
# #         l = []
# #         for it in UserBD.objects.all():
# #             l.append(super(MultiDBModelAdmin, self).get_queryset(request).using(it.username))
# #         # print([i for i in l])
# #         for w in l:
# #             return w
# #
# #     def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
# #         # Tell Django to populate ForeignKey widgets using a query
# #         # on the 'other' database.
# #         return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)
# #
# #     def formfield_for_manytomany(self, db_field, request=None, **kwargs):
# #         # Tell Django to populate ManyToMany widgets using a query
# #         # on the 'other' database.
# #         return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)
# #
# #
# # class ProductAdmin(MultiDBModelAdmin):
# #     form = AdditionalForm
# #
# #     def save_model(self, request, obj, form, change):
# #         name_column, type_column = request.POST['name_column'], request.POST['type_column']
# #         cursor = connections[self.using].cursor()
# #         cursor.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))
# #
# #
# class ClientAdmin(admin.ModelAdmin):
#     pass
# #     # list_display = ['id']
# #     # fields = ('address',)
# #
# # admin.site.register(Product, ProductAdmin)
# admin.site.register(Client, ClientAdmin)
from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    website = models.CharField(max_length=512)
    user = models.ForeignKey('auth.User')
    company_logo = models.ImageField(upload_to='/static/images/')

    class Meta:
        db_table = 'client'

    # def __str__(self):
    #     return "%s" % (self.user.username,)


class UserBD(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    password = models.CharField(max_length=512)

    class Meta:
        db_table = 'user_db'


class Product(models.Model):
    # id = models.AutoField(primary_key=True)
    # user = UserBD.objects.all()

    class Meta:
        managed = False
        db_table = "product"

#
# def update_settings():
#     from django.conf import settings
#     DATABASES = settings.DATABASES
#
#     db = UserBD.objects.all()
#     if db.exists():
#         for user in db:
#             DATABASES.update({user.username: {"NAME": user.title,
#                                      "PASSWORD": user.password,
#                                      "USER": user.username,
#                                      'ENGINE': 'django.db.backends.postgresql',
#                                      'HOST': '127.0.0.1',
#                                     'PORT': '5432',}
#                               })
# update_settings()
from django.db import models
from django.db import connections, ConnectionHandler
from django.db.models.query import QuerySet
# from south.db import db


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


# class ProductQuery(object):
#     def create_con(self):
#         users = UserBD.objects.all()
#         items = []
#         col_name = []
#         for user in users:
#             connections._databases['userdb']['USER'] = user.username
#             connections._databases['userdb']['PASSWORD'] = user.password
#             connections._databases['userdb']['NAME'] = user.title
#             c = connections['userdb'].cursor()
#             c.execute('select * from product')
#             items.append(c.fetchall())
#             c.execute("select column_name from information_schema.columns WHERE table_name = 'product'")
#             col_name.append(c.fetchall())
#         return items, col_name


class Product(models.Model):
    # id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = "product"


def update_settings():
    from django.conf import settings
    DATABASES = settings.DATABASES

    db = UserBD.objects.all()
    if db.exists():
        for user in db:
            if user.title != DATABASES['userdb']['NAME'] and user.title is not None:
                DATABASES['userdb']['NAME'] = user.title
                DATABASES['userdb']['USER'] = user.username
                DATABASES['userdb']['PASSWORD'] = user.password

update_settings()
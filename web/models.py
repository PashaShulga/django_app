from django.db import models
from django.db.utils import ConnectionHandler, ConnectionRouter


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    website = models.CharField(max_length=512)
    user = models.ForeignKey('auth.User')

    class Meta:
        db_table = 'client'

    def __str__(self):
        return "%s" % (self.user.username,)


class UserBD(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    password = models.CharField(max_length=512)

    class Meta:
        db_table = 'user_db'



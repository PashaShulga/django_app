from django.db import models

# Create your models here.


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    website = models.CharField(max_length=512)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'client'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=512)
    email_address = models.CharField(max_length=128)

    def __str__(self):
        return '%s, %s, %s' % (self.username, self.email_address, self.password)

    class Meta:
        db_table = 'user'


# class XLSAdd(models.Model):
#     id = models.AutoField(primary_key=True)
#


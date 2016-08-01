from django.db import models
from django.contrib.auth.models import User, UserManager


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=130)
    address = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.CharField(max_length=520, blank=True)
    user = models.ForeignKey('auth.User')
    company_logo = models.ImageField(blank=True, upload_to='/static/images/')
    contact_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=128, blank=True)

    class Meta:
        db_table = 'client'


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)

    class Meta:
        db_table = "company"
        permissions = (
            ("admin", "Administrator"),
            ("user_short", "User Short"),
            ("user_admin", "User Administrator")
        )


class CustomUser(User):
    CHOICES = (
        (1, "L_Package"),
        (2, "XL_Package")
    )
    company_type = models.IntegerField(choices=CHOICES, default=CHOICES[0][0])
    user = models.ForeignKey('UserBD')
    company = models.ForeignKey('Client')
    primary_root = models.BooleanField(default=False)
    objects = UserManager()

    # class Meta:
    #     db_table = "custom_user"


class Product(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = "product"


class UserBD(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=40)
    title = models.CharField(max_length=40)
    password = models.CharField(max_length=520)

    class Meta:
        managed = True
        db_table = "user_db"


class Charts(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=100)
    columns_name = models.CharField(max_length=512)
    chart_type = models.CharField(max_length=50)
    y_name = models.CharField(max_length=50, blank=True)
    grouping_by = models.CharField(max_length=50)
    company = models.ForeignKey("Client")

    class Meta:
        db_table = "charts"


class UserDatafiles(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('CustomUser')
    table_name = models.CharField(max_length=100)


def update_settings():
    from django.conf import settings
    DATABASES = settings.DATABASES
    try:

        db = UserBD.objects.all()
        if db.exists():
            for user in db:
                DATABASES.update({user.username: {"NAME": user.title,
                                                  "PASSWORD": user.password,
                                                  "USER": user.username,
                                                  'ENGINE': 'django.db.backends.postgresql',
                                                  'HOST': '127.0.0.1',
                                                  'PORT': '5432',}
                                  })
    except Exception as e:
        print(e)


# update_settings()
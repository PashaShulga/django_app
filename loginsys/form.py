from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from web.models import CustomUser
from django.db import connections
from web.models import UserBD


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.CharField(label="",
                               max_length=30,
                               strip=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username',
                                                             'required': True})
    )
    email1 = forms.EmailField(label="",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail', 'required': True}))

    company_title = forms.CharField(label="", max_length=128,
                                    strip=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Company Title',
                                                                  'required': True}))

    password1 = forms.CharField(label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True}))

    password2 = forms.CharField(label="",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password againe", 'required': True}),
        strip=False)

    CHOICES = (
        (1, "L Package"),
        (2, "XL Package"),
    )

    company_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

    class Meta:
        model = User
        exclude = ("id", "last_login", "is_superuser", "first_name", "last_name",
                   "is_staff", "is_active", "date_joined", 'user_permissions', "groups", "email", "password")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        print(user)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email1"]
        user.company_type = self.cleaned_data["company_type"]
        user.company_title = self.cleaned_data["company_title"]
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label="", max_length=254,
                                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                                      'placeholder': 'Email of Username'}))


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class ChangePassForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("Warning! The two password fields didn't match."),
        }
    old_password = forms.CharField(label=("Old password"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password againe'}))

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class ChangeAdminPassword(forms.Form):
    error_messages = {
        'password_mismatch': ("Warning! The two password fields didn't match."),
        }
    CHOICES = ((it.id, it.username) for it in CustomUser.objects.all())
    username = forms.ChoiceField(choices=CHOICES)

    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password againe'}))
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class AuthenticationForm(forms.Form):
    username = forms.CharField(label="", max_length=30, strip=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label="", strip=False,
                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"}))

    def clean_password2(self):
        password = self.cleaned_data["password"]
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password'), self.instance)
        return password


class ModifyProfile(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    first_name = forms.CharField(label="", max_length=30, strip=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=30, strip=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    company = forms.CharField(label="", max_length=30, strip=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}))


class UploadFileForm(forms.Form):
    CHOICES = (
        ("xls", "xls"),
        ("csv", "csv")
    )
    table_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Table name'}))
    file_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)
    file = forms.FileField(label='Choose the file', widget=forms.FileInput(attrs={"name": "file"}))


class AdditionalForm(forms.Form):
    table_name = forms.CharField(label='Table name', max_length=30)
    name_column = forms.CharField(label='Column name', max_length=30)
    type_column = forms.CharField(label='Column type', max_length=30)
    # CHOICES = ((it.username, it.username) for it in UserBD.objects.all())
    # user = forms.ChoiceField(choices=CHOICES)


class AddNewUser(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.CharField(label="",
                               max_length=30,
                               strip=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username',
                                                             'required': True})
    )
    email = forms.EmailField(label="",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail', 'required': True}))

    password1 = forms.CharField(label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True}))

    password2 = forms.CharField(label="",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password again", 'required': True}),
        strip=False)

    CHOICES = (
        ("M", "Manager"),
        ("E", "Employee")
    )

    roles = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class AddAdminUser(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.CharField(label="",
                               max_length=30,
                               strip=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username',
                                                             'required': True})
    )

    password1 = forms.CharField(label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True}))

    password2 = forms.CharField(label="",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password again", 'required': True}),
        strip=False)


class EditCompany(forms.Form):
    company_name = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Company name", "readonly":True}))
    address = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Address"}))
    postal_code = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Postal code"}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Phone"}))
    website = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Website"}))


class EditUser(forms.Form):
    username = forms.CharField(max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username", "required": True}))
    first_name = forms.CharField(max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "First Name", "required": True}))
    last_name = forms.CharField(max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Last Name", "required": True}))
    email = forms.CharField(max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Email", "required": True}))
    set_user_id = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'set_user_id'}))
    CHOICES = (
        ("M", "Manager"),
        ("E", "Employee")
    )
    roles = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)


class AddCompany(EditCompany):
    company_name = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Company name", "readonly":False}))
    email = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Email"}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Address", "rows": "2"}))
    contact_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Contact"}))

    CHOICES_PACKAGE = (
        (1, "Package L (only charts)"),
        (2, "Package XL (with collect and charts)")
    )

    CHOICES_UPDATE = (
        ("d", "Day"),
        ("w", "Week"),
        ("m", "Month"),
        ("q", "Quarter"),
        ("h_y", "Half Year"),
        ("y", "Year")
    )

    package = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES_PACKAGE)
    update = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES_UPDATE)

    # CHOICE = ((u.id, u.username) for u in UserBD.objects.all())
    # who_is_admin = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICE)

    username = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username"}))

    password1 = forms.CharField(label="", required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True}))

    password2 = forms.CharField(label="", required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password againe", 'required': True}),
        strip=False)


class ChangeCompany(forms.Form):
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Phone"}))
    company_name = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Company name"}))
    email = forms.CharField(required=True, max_length=130, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Email"}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Address", "rows": "2"}))
    contact_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Contact"}))


class ChangeCompanyPackage(forms.Form):
    CHOICES_PACKAGE = (
        (1, "Package L (only charts)"),
        (2, "Package XL (with collect and charts)")
    )

    CHOICES_UPDATE = (
        ("d", "Day"),
        ("w", "Week"),
        ("m", "Month"),
        ("q", "Quarter"),
        ("h_y", "Half Year"),
        ("y", "Year")
    )

    package = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES_PACKAGE)
    update = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES_UPDATE)